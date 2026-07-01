import { describe, it, expect, beforeEach, vi } from 'vitest'
import { registry } from './plugin-registry'

const ID = 'test:plugin'
const DUP_ID = 'test:dup'
const PRIORITY_LOW = 'test:low'
const PRIORITY_HIGH = 'test:high'

function cleanup() {
  for (const id of [ID, DUP_ID, PRIORITY_LOW, PRIORITY_HIGH]) {
    try { registry.unregisterPlugin(id) } catch {}
  }
}

beforeEach(cleanup)

describe('PluginRegistry', () => {
  it('registers a plugin to the specified slot', () => {
    registry.registerPlugin({
      id: ID,
      name: 'Test',
      slots: { 'activity:action': { component: {} as any } },
    })
    const regs = registry.getSlotRegistrations('activity:action')
    expect(regs).toHaveLength(1)
    expect(regs[0].id).toBe(ID)
  })

  it('returns empty array for unregistered slot', () => {
    expect(registry.getSlotRegistrations('status-bar')).toEqual([])
  })

  it('sorts registrations by priority ascending', () => {
    registry.registerPlugin({
      id: PRIORITY_LOW,
      name: 'Low',
      slots: { 'activity:action': { component: {} as any, priority: 20 } },
    })
    registry.registerPlugin({
      id: PRIORITY_HIGH,
      name: 'High',
      slots: { 'activity:action': { component: {} as any, priority: 10 } },
    })
    const regs = registry.getSlotRegistrations('activity:action')
    expect(regs[0].id).toBe(PRIORITY_HIGH)
    expect(regs[1].id).toBe(PRIORITY_LOW)
  })

  it('removes plugin from all slots on unregisterPlugin', () => {
    registry.registerPlugin({
      id: ID,
      name: 'Test',
      slots: {
        'activity:action': { component: {} as any },
        'sidebar:panel': { component: {} as any, panelId: 'x' },
      },
    })
    registry.unregisterPlugin(ID)
    expect(registry.getSlotRegistrations('activity:action')).toEqual([])
    expect(registry.getSlotRegistrations('sidebar:panel')).toEqual([])
  })

  it('warns on duplicate id and does not double-register', () => {
    const warn = vi.spyOn(console, 'warn').mockImplementation(() => {})
    registry.registerPlugin({
      id: DUP_ID,
      name: 'First',
      slots: { 'activity:action': { component: {} as any } },
    })
    registry.registerPlugin({
      id: DUP_ID,
      name: 'Second',
      slots: { 'activity:action': { component: {} as any } },
    })
    expect(warn).toHaveBeenCalledWith(expect.stringContaining(DUP_ID))
    expect(registry.getSlotRegistrations('activity:action')).toHaveLength(1)
    warn.mockRestore()
  })

  it('registers hooks and runs them via runHook', async () => {
    const handler = vi.fn(async (ctx: any, next: any) => next(ctx))
    registry.registerPlugin({
      id: 'test:hook',
      name: 'Hook',
      hooks: { 'message:before-send': handler },
    })
    await registry.runHook('message:before-send', { value: 1 })
    expect(handler).toHaveBeenCalled()
    registry.unregisterPlugin('test:hook')
  })
})
