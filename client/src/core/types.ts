import type { Component } from 'vue'

/** 固定 slot 词汇表——框架定义，插件不能发明 */
export type SlotName =
  | 'activity:action'
  | 'activity:settings'
  | 'sidebar:panel'
  | 'sidebar:header-action'
  | 'sidebar:footer'
  | 'main:header'
  | 'main:header-action'
  | 'chat:messages'
  | 'chat:input'
  | 'chat:input-toolbar'
  | 'dialog'
  | 'status-bar'

/** 固定 hook 词汇表——框架定义，插件不能发明 */
export type HookName =
  | 'message:before-send'
  | 'message:before-render'
  | 'tool:before-execute'
  | 'tool:after-execute'

/** 插件注册到某个 slot 的完整信息 */
export interface SlotRegistration {
  /** 插件 id（唯一） */
  id: string
  /** Vue 组件 */
  component: Component
  /** 排序权重，越小越靠前（默认 100） */
  priority: number
  /**
   * sidebar:panel 专用
   * activity:action 通过 panelId 关联到对应的 sidebar:panel
   */
  panelId?: string
  /** sidebar:panel 专用：面板显示名 */
  panelLabel?: string
  /** activity:action 专用：图标组件 */
  icon?: Component
}

/** 插件声明时的 slot 配置（精简，id 和 priority 由注册中心补齐） */
export interface PluginSlotConfig {
  component: Component
  priority?: number
  panelId?: string
  panelLabel?: string
  icon?: Component
}

/** Hook handler 签名——middleware 模式 */
export interface HookHandler {
  (ctx: any, next: () => Promise<any>): Promise<any>
}

/** 插件定义 */
export interface PluginDefinition {
  id: string
  name: string
  description?: string
  slots?: Partial<Record<SlotName, PluginSlotConfig>>
  hooks?: Partial<Record<HookName, HookHandler>>
}
