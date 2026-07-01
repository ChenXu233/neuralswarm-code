<script setup lang="ts">
import { computed } from 'vue'
import type { SlotName } from './types'
import { getSlotRegistrations } from './plugin-registry'

const props = defineProps<{
  name: SlotName
}>()

const registrations = computed(() => getSlotRegistrations(props.name))
</script>

<template>
  <template v-for="reg in registrations" :key="reg.id">
    <component :is="reg.component" v-bind="$attrs" />
  </template>
</template>
