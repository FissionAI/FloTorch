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
  mutationFn: async () => {
    const response = await useFetchAllKbModels()
    selectedModel.value = props.selectedValue;
    modelsList.value = response.map(model=>{
      return {
        ...model,
      label : model.name,
      value : model.kb_id
      }
   
    });
    return response
  }
})

onMounted(() => {
  fetchAllKbModels(props.modelName as string)
})

</script>

<template>

  <div class="flex gap-2">
    <UFormField name="kb_data" label=" Knowledge base data " class="flex-11 text-ellipsis overflow-hidden">
       <USelectMenu v-model="selectedModel" :loading="isLoading" :items="modelsList" multiple  class="w-full my-1" value-key="value" @change="emit('kbModels', {value:selectedModel})" />
    </UFormField>
        <UFormField name="refetch_kb_model" label=" " class="flex-1">
        <UButton
          label="Fetch Kb Model"
          trailing-icon="i-lucide-repeat-2"
          class=""
          @click.prevent="fetchAllKbModels()"
        />
        <template #hint>
          <FieldTooltip field-name="kb_data" />
        </template>
      </UFormField>
    </div>

</template>