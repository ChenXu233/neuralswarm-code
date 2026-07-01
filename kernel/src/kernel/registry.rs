use std::collections::HashMap;
use std::sync::Arc;
use anyhow::{Result, anyhow};
use crate::kernel::handler::Handler;

/// MVP 固定词汇表
pub const VALID_POINTS: &[&str] = &[
    "user-message",
    "llm-prompt",
    "llm-response",
    "tool-execute.before",
    "tool-execute.after",
    "tool-result",
    "tool:file_read",
    "tool:file_write",
    "tool:shell",
    "lifecycle:start",
    "lifecycle:stop",
];

pub struct HandlerRegistration {
    pub id: String,
    pub handler: Arc<dyn Handler>,
    pub before: Vec<String>,
    pub after: Vec<String>,
}

struct PointEntry {
    name: String,
    registrations: Vec<HandlerRegistration>,
    /// 缓存排好序的 handler 列表
    sorted: Vec<Arc<dyn Handler>>,
}

pub struct Registry {
    points: HashMap<String, PointEntry>,
}

impl Registry {
    pub fn new() -> Self {
        let mut points = HashMap::new();
        for name in VALID_POINTS {
            points.insert(name.to_string(), PointEntry {
                name: name.to_string(),
                registrations: Vec::new(),
                sorted: Vec::new(),
            });
        }
        Registry { points }
    }

    /// 注册一个 handler 到点上。
    /// 如果 point 不在词汇表里 → 返回错误。
    pub fn register(&mut self, point: &str, reg: HandlerRegistration) -> Result<()> {
        let entry = self.points.get_mut(point)
            .ok_or_else(|| anyhow!("unknown point: '{}'. valid points: {:?}", point, VALID_POINTS))?;

        // 检查 before/after 引用的 handler id 是否存在（同点内）
        for before_id in &reg.before {
            if !entry.registrations.iter().any(|r| r.id == *before_id) {
                return Err(anyhow!("before '{}' not found in point '{}'", before_id, point));
            }
        }
        for after_id in &reg.after {
            if !entry.registrations.iter().any(|r| r.id == *after_id) {
                return Err(anyhow!("after '{}' not found in point '{}'", after_id, point));
            }
        }

        entry.registrations.push(reg);
        self.sort_handlers(point)?;

        Ok(())
    }

    /// 取排好序的 handler 列表
    pub fn get_handlers(&self, point: &str) -> Result<&[Arc<dyn Handler>]> {
        let entry = self.points.get(point)
            .ok_or_else(|| anyhow!("unknown point: '{}'", point))?;
        Ok(&entry.sorted)
    }

    fn sort_handlers(&mut self, point: &str) -> Result<()> {
        let entry = self.points.get(point)
            .ok_or_else(|| anyhow!("unknown point: '{}'", point))?;

        // Kahn 拓扑排序
        let n = entry.registrations.len();
        let ids: Vec<&str> = entry.registrations.iter().map(|r| r.id.as_str()).collect();
        let mut in_degree = vec![0usize; n];
        let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];

        for (i, reg) in entry.registrations.iter().enumerate() {
            for before_id in &reg.before {
                if let Some(j) = ids.iter().position(|id| *id == before_id) {
                    adj[j].push(i);
                    in_degree[i] += 1;
                }
            }
            for after_id in &reg.after {
                if let Some(j) = ids.iter().position(|id| *id == after_id) {
                    adj[i].push(j);
                    in_degree[j] += 1;
                }
            }
        }

        let mut queue: Vec<usize> = in_degree.iter()
            .enumerate()
            .filter(|(_, &d)| d == 0)
            .map(|(i, _)| i)
            .collect();

        let mut sorted = Vec::new();
        let mut idx = 0;
        while idx < queue.len() {
            let i = queue[idx];
            idx += 1;
            sorted.push(i);
            for &j in &adj[i] {
                in_degree[j] -= 1;
                if in_degree[j] == 0 {
                    queue.push(j);
                }
            }
        }

        if sorted.len() != n {
            return Err(anyhow!("circular dependency detected in point '{}'", point));
        }

        let entry = self.points.get_mut(point).unwrap();
        entry.sorted = sorted.iter().map(|&i| entry.registrations[i].handler.clone()).collect();

        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::kernel::context::Context;

    struct NoopHandler;
    #[async_trait::async_trait]
    impl Handler for NoopHandler {
        async fn invoke(&self, ctx: Context) -> anyhow::Result<Context> { Ok(ctx) }
    }

    #[test]
    fn test_unknown_point_rejected() {
        let mut reg = Registry::new();
        let result = reg.register("invalid-point", HandlerRegistration {
            id: "test".into(),
            handler: Arc::new(NoopHandler),
            before: vec![],
            after: vec![],
        });
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("unknown point"));
    }

    #[test]
    fn test_valid_points_accepted() {
        let mut reg = Registry::new();
        for point in VALID_POINTS {
            let result = reg.register(point, HandlerRegistration {
                id: format!("handler-{}", point),
                handler: Arc::new(NoopHandler),
                before: vec![],
                after: vec![],
            });
            assert!(result.is_ok(), "should accept point '{}'", point);
        }
    }

    #[test]
    fn test_topological_order() {
        let mut reg = Registry::new();
        reg.register("llm-prompt", HandlerRegistration {
            id: "first".into(),
            handler: Arc::new(NoopHandler),
            before: vec![],
            after: vec![],
        }).unwrap();
        reg.register("llm-prompt", HandlerRegistration {
            id: "second".into(),
            handler: Arc::new(NoopHandler),
            before: vec![],
            after: vec!["first".into()],
        }).unwrap();

        let handlers = reg.get_handlers("llm-prompt").unwrap();
        assert_eq!(handlers.len(), 2);
    }
}
