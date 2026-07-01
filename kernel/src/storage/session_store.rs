use std::sync::Mutex;
use rusqlite::Connection;

/// 存储层消息结构（可序列化为 JSON，与 context::Message 互转）
#[derive(Debug, Clone)]
pub struct StoredMessage {
    pub role: String,
    pub content: String,
    pub tool_calls: Option<Vec<crate::kernel::context::ToolCall>>,
    pub tool_call_id: Option<String>,
}

#[derive(Debug, Clone)]
pub struct SessionRecord {
    pub id: String,
    pub workspace_path: String,
    pub created_at: String,
    pub updated_at: String,
    pub message_count: i64,
}

#[derive(Debug, Clone)]
pub struct WorkspaceInfo {
    pub path: String,
    pub last_active: String,
    pub session_count: i64,
}

/// SQLite 会话存储。线程安全，内部用 Mutex。
pub struct SessionStore {
    conn: Mutex<Connection>,
}

impl SessionStore {
    /// 创建或打开 SQLite 数据库。
    /// path: 数据库文件路径（如 "data/neuralswarm.db"）。
    /// 父目录不存在会自动创建。
    pub fn new(path: &str) -> anyhow::Result<Self> {
        if let Some(parent) = std::path::Path::new(path).parent() {
            if !parent.as_os_str().is_empty() {
                std::fs::create_dir_all(parent)?;
            }
        }
        let conn = Connection::open(path)?;

        // 建表
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                workspace_path TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id),
                role TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                tool_calls TEXT,
                tool_call_id TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, id);
            "
        )?;

        Ok(SessionStore { conn: Mutex::new(conn) })
    }

    /// 创建新会话。
    pub fn create_session(&self, id: &str, workspace_path: &str) -> anyhow::Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute(
            "INSERT INTO sessions (id, workspace_path) VALUES (?1, ?2)",
            rusqlite::params![id, workspace_path],
        )?;
        Ok(())
    }

    /// 获取会话信息。
    pub fn get_session(&self, id: &str) -> anyhow::Result<Option<SessionRecord>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT s.id, s.workspace_path, s.created_at, s.updated_at,
                    COALESCE(COUNT(m.id), 0) as message_count
             FROM sessions s
             LEFT JOIN messages m ON m.session_id = s.id
             WHERE s.id = ?1
             GROUP BY s.id"
        )?;

        let mut rows = stmt.query(rusqlite::params![id])?;
        match rows.next()? {
            Some(row) => Ok(Some(SessionRecord {
                id: row.get(0)?,
                workspace_path: row.get(1)?,
                created_at: row.get(2)?,
                updated_at: row.get(3)?,
                message_count: row.get(4)?,
            })),
            None => Ok(None),
        }
    }

    /// 列出所有会话。
    pub fn list_sessions(&self) -> anyhow::Result<Vec<SessionRecord>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT s.id, s.workspace_path, s.created_at, s.updated_at,
                    COALESCE(COUNT(m.id), 0) as message_count
             FROM sessions s
             LEFT JOIN messages m ON m.session_id = s.id
             GROUP BY s.id
             ORDER BY s.updated_at DESC"
        )?;

        let rows = stmt.query_map([], |row| {
            Ok(SessionRecord {
                id: row.get(0)?,
                workspace_path: row.get(1)?,
                created_at: row.get(2)?,
                updated_at: row.get(3)?,
                message_count: row.get(4)?,
            })
        })?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row?);
        }
        Ok(result)
    }

    /// 添加消息到会话。
    pub fn add_message(&self, session_id: &str, msg: &StoredMessage) -> anyhow::Result<()> {
        let conn = self.conn.lock().unwrap();

        // 序列化 tool_calls 为 JSON 字符串
        let tool_calls_json = msg.tool_calls.as_ref()
            .map(|tc| serde_json::to_string(tc).unwrap_or_default());

        conn.execute(
            "INSERT INTO messages (session_id, role, content, tool_calls, tool_call_id) VALUES (?1, ?2, ?3, ?4, ?5)",
            rusqlite::params![
                session_id,
                msg.role,
                msg.content,
                tool_calls_json,
                msg.tool_call_id,
            ],
        )?;

        // 更新 sessions.updated_at
        conn.execute(
            "UPDATE sessions SET updated_at = datetime('now') WHERE id = ?1",
            rusqlite::params![session_id],
        )?;

        Ok(())
    }

    /// 获取会话的所有消息。
    pub fn get_messages(&self, session_id: &str) -> anyhow::Result<Vec<StoredMessage>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT role, content, tool_calls, tool_call_id
             FROM messages
             WHERE session_id = ?1
             ORDER BY id ASC"
        )?;

        let rows = stmt.query_map(rusqlite::params![session_id], |row| {
            let role: String = row.get(0)?;
            let content: String = row.get(1)?;
            let tool_calls_str: Option<String> = row.get(2)?;
            let tool_call_id: Option<String> = row.get(3)?;

            // 反序列化 tool_calls
            let tool_calls = tool_calls_str
                .and_then(|s| serde_json::from_str::<Vec<crate::kernel::context::ToolCall>>(&s).ok());

            Ok(StoredMessage { role, content, tool_calls, tool_call_id })
        })?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row?);
        }
        Ok(result)
    }

    /// 删除会话及其所有消息。
    pub fn delete_session(&self, id: &str) -> anyhow::Result<()> {
        let conn = self.conn.lock().unwrap();
        conn.execute("DELETE FROM messages WHERE session_id = ?1", rusqlite::params![id])?;
        conn.execute("DELETE FROM sessions WHERE id = ?1", rusqlite::params![id])?;
        Ok(())
    }

    /// 按 workspace_path 聚合，返回去重的工作区列表。
    pub fn list_workspaces(&self) -> anyhow::Result<Vec<WorkspaceInfo>> {
        let conn = self.conn.lock().unwrap();
        let mut stmt = conn.prepare(
            "SELECT workspace_path, MAX(updated_at) as last_active, COUNT(*) as session_count
             FROM sessions
             GROUP BY workspace_path
             ORDER BY last_active DESC"
        )?;

        let rows = stmt.query_map([], |row| {
            Ok(WorkspaceInfo {
                path: row.get(0)?,
                last_active: row.get(1)?,
                session_count: row.get(2)?,
            })
        })?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row?);
        }
        Ok(result)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_and_get_session() {
        let store = SessionStore::new(":memory:").unwrap();
        store.create_session("test-1", "/home/user/proj").unwrap();
        let session = store.get_session("test-1").unwrap().unwrap();
        assert_eq!(session.id, "test-1");
        assert_eq!(session.workspace_path, "/home/user/proj");
    }

    #[test]
    fn test_add_and_get_messages() {
        let store = SessionStore::new(":memory:").unwrap();
        store.create_session("test-1", "/tmp").unwrap();

        let msg1 = StoredMessage {
            role: "user".into(),
            content: "hello".into(),
            tool_calls: None,
            tool_call_id: None,
        };
        let msg2 = StoredMessage {
            role: "assistant".into(),
            content: "Hi!".into(),
            tool_calls: None,
            tool_call_id: None,
        };

        store.add_message("test-1", &msg1).unwrap();
        store.add_message("test-1", &msg2).unwrap();

        let messages = store.get_messages("test-1").unwrap();
        assert_eq!(messages.len(), 2);
        assert_eq!(messages[0].content, "hello");
        assert_eq!(messages[1].content, "Hi!");
    }

    #[test]
    fn test_delete_session() {
        let store = SessionStore::new(":memory:").unwrap();
        store.create_session("test-1", "/tmp").unwrap();
        store.delete_session("test-1").unwrap();
        let session = store.get_session("test-1").unwrap();
        assert!(session.is_none());
    }

    #[test]
    fn test_list_sessions() {
        let store = SessionStore::new(":memory:").unwrap();
        store.create_session("a", "/a").unwrap();
        store.create_session("b", "/b").unwrap();
        let list = store.list_sessions().unwrap();
        assert_eq!(list.len(), 2);
    }

    #[test]
    fn test_get_session_not_found() {
        let store = SessionStore::new(":memory:").unwrap();
        let session = store.get_session("nonexistent").unwrap();
        assert!(session.is_none());
    }

    #[test]
    fn test_list_workspaces() {
        let store = SessionStore::new(":memory:").unwrap();
        store.create_session("s1", "/home/user/proj-a").unwrap();
        store.create_session("s2", "/home/user/proj-a").unwrap();
        store.create_session("s3", "/home/user/proj-b").unwrap();
        let ws = store.list_workspaces().unwrap();
        assert_eq!(ws.len(), 2);
        assert_eq!(
            ws.iter().find(|w| w.path == "/home/user/proj-a").unwrap().session_count,
            2
        );
    }
}
