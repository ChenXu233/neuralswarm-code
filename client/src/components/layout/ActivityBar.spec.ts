import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import ActivityBar from './ActivityBar.vue'
import { registry } from '@/core/plugin-registry'

function cleanup() {
  try { registry.unregisterPlugin('test:panel') } catch {}
  try { registry.unregisterPlugin('test:settings') } catch {}
}

beforeEach(cleanup)

describe('ActivityBar', () => {
  it('renders action buttons from registry', () => {
    registry.registerPlugin({
      id: 'test:panel',
      name: 'Test Panel',
      slots: {
        'activity:action': {
          component: { template: '<span>Icon</span>' },
          panelId: 'test',
          priority: 10,
          icon: { template: '<span>T</span>' },
        },
      },
    })
    const wrapper = mount(ActivityBar, {
      props: { activePanel: null, showSettings: false },
    })
    expect(wrapper.findAll('.activity-btn').length).toBeGreaterThanOrEqual(1)
  })

  it('highlights the active panel button', () => {
    registry.registerPlugin({
      id: 'test:panel',
      name: 'Test Panel',
      slots: {
        'activity:action': {
          component: { template: '<span>Icon</span>' },
          panelId: 'test',
          priority: 10,
          icon: { template: '<span>T</span>' },
        },
      },
    })
    const wrapper = mount(ActivityBar, {
      props: { activePanel: 'test', showSettings: false },
    })
    expect(wrapper.find('.activity-btn.active').exists()).toBe(true)
  })

  it('emits update:activePanel on action button click', async () => {
    registry.registerPlugin({
      id: 'test:panel',
      name: 'Test Panel',
      slots: {
        'activity:action': {
          component: { template: '<span>Icon</span>' },
          panelId: 'test',
          priority: 10,
          icon: { template: '<span>T</span>' },
        },
      },
    })
    const wrapper = mount(ActivityBar, {
      props: { activePanel: null, showSettings: false },
    })
    await wrapper.find('.top-icons .activity-btn').trigger('click')
    expect(wrapper.emitted('update:activePanel')).toBeTruthy()
  })

  it('emits toggleSettings on settings button click', async () => {
    registry.registerPlugin({
      id: 'test:settings',
      name: 'Settings',
      slots: {
        'activity:settings': {
          component: { template: '<span>Gear</span>' },
          priority: 10,
        },
      },
    })
    const wrapper = mount(ActivityBar, {
      props: { activePanel: null, showSettings: false },
    })
    await wrapper.find('.bottom-icons .activity-btn').trigger('click')
    expect(wrapper.emitted('toggleSettings')).toBeTruthy()
  })
})
