import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import PluginSlot from './plugin-slot.vue'
import { registry } from './plugin-registry'

function cleanup() {
  try { registry.unregisterPlugin('test:a') } catch {}
  try { registry.unregisterPlugin('test:b') } catch {}
}

beforeEach(cleanup)

describe('PluginSlot', () => {
  it('renders nothing for empty slot', () => {
    const wrapper = mount(PluginSlot, { props: { name: 'status-bar' } })
    expect(wrapper.findAll('*')).toHaveLength(0)
  })

  it('renders all registered components in order', () => {
    registry.registerPlugin({
      id: 'test:a',
      name: 'A',
      slots: { 'activity:action': { component: { template: '<button>A</button>' } } },
    })
    registry.registerPlugin({
      id: 'test:b',
      name: 'B',
      slots: { 'activity:action': { component: { template: '<button>B</button>' } } },
    })
    const wrapper = mount(PluginSlot, { props: { name: 'activity:action' } })
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(2)
    expect(buttons[0].text()).toBe('A')
    expect(buttons[1].text()).toBe('B')
  })

  it('passes $attrs to registered components', () => {
    registry.registerPlugin({
      id: 'test:a',
      name: 'A',
      slots: { 'sidebar:panel': { component: { template: '<div>{{ $attrs.dataAttr }}</div>' } } },
    })
    const wrapper = mount(PluginSlot, {
      props: { name: 'sidebar:panel', dataAttr: 'passed' },
    })
    expect(wrapper.text()).toContain('passed')
  })
})
