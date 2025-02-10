<script setup lang="ts">

const { $emit } = useNuxtApp()

const props = defineProps<{
  fieldName: keyof typeof useTooltipInfo
}>()

const setTooltipInfo = computed(() => {
  return useTooltipInfo[props.fieldName];
})

const emitTooltip = () => {
  $emit('showTooltip', {tooltip: setTooltipInfo, fieldName: props.fieldName})
}

</script>



<template>
    <p class="info-tooltip ml-4" @click="emitTooltip">
      info
    </p>
</template>
