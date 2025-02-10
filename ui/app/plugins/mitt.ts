import mitt from 'mitt'
import { defineNuxtPlugin } from '#app'

export default defineNuxtPlugin(() => {
  const emitter = mitt()

  return {
    provide: {
      emit: emitter.emit,    // Will be available as this.$emit
      on: emitter.on,        // Will be available as this.$on
      off: emitter.off,      // Will be available as this.$off
    },
  }
}) 