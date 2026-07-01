import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Sidebar from './Sidebar.vue'
import { registry } from '@/core/plugin-registry'

function cleanup() {
  try { registry.unregisterPlugin('test:panel') } catch {}
}

beforeEach(cleanup)

describe('Sidebar', () => {
  it('renders the panel component matching panelId', () => {
    registry.registerPlugin({
      id: 'test:panel',
      name: 'Test Panel',
      slots: {
        'sidebar:panel': {
          component: { template: '<div>Panel Content</div>' },
          panelId: 'test',
          panelLabel: 'Test Panel',
          priority: 10,
        },
      },
    })
    const wrapper = mount(Sidebar, { props: { panelId: 'test' } })
    expect(wrapper.text()).toContain('Panel Content')
  })

  it('displays panelLabel in sidebar header', () => {
    registry.registerPlugin({
      id: 'test:panel',
      name: 'Test Panel',
      slots: {
        'sidebar:panel': {
          component: { template: '<div>Content</div>' },
          panelId: 'test',
          panelLabel: 'My Panel',
          priority: 10,
        },
      },
    })
    const wrapper = mount(Sidebar, { props: { panelId: 'test' } })
    expect(wrapper.find('.sidebar-title').text()).toBe('My Panel')
  })

  it('renders nothing for unmatched panelId', () => {
    const wrapper = mount(Sidebar, { props: { panelId: 'nonexistent' } })
    expect(wrapper.find('.sidebar').exists()).toBe(false)
  })

  it('passes $attrs to the panel component', () => {
    registry.registerPlugin({
      id: 'test:panel',
      name: 'Test Panel',
      slots: {
        'sidebar:panel': {
          component: { template: '<div>{{ $attrs.customProp }}</div>' },
          panelId: 'test',
          panelLabel: 'Test',
          priority: 10,
        },
      },
    })
    const wrapper = mount(Sidebar, {
      props: { panelId: 'test', customProp: 'hello' },
    })
    expect(wrapper.text()).toContain('hello')
  })
})
