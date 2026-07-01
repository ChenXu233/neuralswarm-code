import type {
  SlotName, HookName, SlotRegistration,
  PluginDefinition, HookHandler,
} from './types'

class PluginRegistry {
  private slots = new Map<SlotName, SlotRegistration[]>()
  private hooks = new Map<HookName, HookHandler[]>()
  private pluginIds = new Set<string>()

  registerPlugin(def: PluginDefinition): void {
    if (this.pluginIds.has(def.id)) {
      console.warn(`[PluginRegistry] Duplicate plugin: ${def.id}`)
      return
    }
    this.pluginIds.add(def.id)

    if (def.slots) {
      for (const [slotName, config] of Object.entries(def.slots)) {
        this.registerSlot(slotName as SlotName, {
          id: def.id,
          component: config!.component,
          priority: config!.priority ?? 100,
          panelId: config!.panelId,
          panelLabel: config!.panelLabel,
          icon: config!.icon,
        })
      }
    }

    if (def.hooks) {
      for (const [hookName, handler] of Object.entries(def.hooks)) {
        this.registerHook(hookName as HookName, handler!)
      }
    }
  }

  unregisterPlugin(pluginId: string): void {
    this.pluginIds.delete(pluginId)
    for (const [slot] of this.slots) {
      this.slots.set(
        slot,
        this.slots.get(slot)!.filter(r => r.id !== pluginId),
      )
    }
    for (const [hook] of this.hooks) {
      this.hooks.set(
        hook,
        this.hooks.get(hook)!.filter(h => h !== this.hooks.get(hook)!.find(
          (_, i) => this.hooks.get(hook)![i] === h,
        )),
      )
    }
  }

  private registerSlot(slot: SlotName, reg: SlotRegistration): void {
    if (!this.slots.has(slot)) {
      this.slots.set(slot, [])
    }
    this.slots.get(slot)!.push(reg)
    this.slots.get(slot)!.sort((a, b) => a.priority - b.priority)
  }

  getSlotRegistrations(slot: SlotName): SlotRegistration[] {
    return this.slots.get(slot) ?? []
  }

  private registerHook(hook: HookName, handler: HookHandler): void {
    if (!this.hooks.has(hook)) {
      this.hooks.set(hook, [])
    }
    this.hooks.get(hook)!.push(handler)
  }

  async runHook(hook: HookName, ctx: any): Promise<any> {
    const handlers = this.hooks.get(hook) ?? []
    let current = ctx
    for (const handler of handlers) {
      current = await handler(current, async (nextCtx?: any) => {
        current = nextCtx ?? current
      })
    }
    return current
  }

  getRegisteredPlugins(): string[] {
    return Array.from(this.pluginIds)
  }

  getActiveSlots(): SlotName[] {
    return Array.from(this.slots.keys())
  }
}

/** 全局单例 */
export const registry = new PluginRegistry()

/** 便捷注册函数 */
export function registerPlugin(def: PluginDefinition): void {
  registry.registerPlugin(def)
}

export function getSlotRegistrations(slot: SlotName): SlotRegistration[] {
  return registry.getSlotRegistrations(slot)
}

export async function runHook(hook: HookName, ctx: any): Promise<any> {
  return registry.runHook(hook, ctx)
}
