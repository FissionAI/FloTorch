<script setup lang="ts">
import { useQuery, useMutation } from '@tanstack/vue-query';

const modelValue = defineModel<string>()

const props = defineProps<{
    modelName : string,
    selectedValue : string;
}>()

const emit = defineEmits(['kbModels']);

const modelsList = ref([])
const selectedModel = ref('')

const { mutateAsync: fetchAllKbModels, isPending: isLoading } = useMutation({
  mutationFn: async (modelName: string) => {
    const response = await useFetchAllKbModels(modelName)
    selectedModel.value = props.selectedValue;
    modelsList.value = response;
    console.log('the model data is : ',response)
    return response
  }
})

onMounted(() => {
  fetchAllKbModels(props.modelName as string)
})

</script>

<template>
       <USelectMenu v-model="selectedModel" :loading="isLoading" :items="modelsList" multiple  class="w-full" value-key="value" @change="emit('kbModels', {value:selectedModel})" />
</template>