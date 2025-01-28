<script setup lang="ts">
import { useMutation } from '@tanstack/vue-query';

const props = defineProps<{
    selectedValue : any;
    region : string;
}>()

const emit = defineEmits(['kbModels']);

const modelsList = ref([])
const selectedModel = ref('')

watch(
  () => props.region,
  () => {
    fetchAllKbModels()
  }
)

const { mutateAsync: fetchAllKbModels, isPending: isLoading } = useMutation({
  mutationFn: async () => {
    const response = await useFetchAllKbModels(props.region)
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
  if(!props.region){
    return;
  }
  fetchAllKbModels(props.modelName as string)
})

</script>

<template>

  <div class="flex gap-2">
    <UFormField name="kb_data" label=" Bedrock Knowledge Base Data " class="flex-11 text-ellipsis overflow-hidden" required>
       <USelectMenu :disabled="!props.region" v-model="selectedModel" :loading="isLoading" :items="modelsList" multiple  class="w-full my-1" value-key="value" @change="emit('kbModels', {value:selectedModel})" />
        <p class="my-2 text-red-500" v-if="!props.region">Please select region first </p>
    </UFormField>
        <UFormField name="refetch_kb_model" label=" " class="flex-1" >
        <UButton
          label="Fetch Bedrock Kb"
          trailing-icon="i-lucide-repeat-2"
          :disabled="!props.region"
          @click.prevent="fetchAllKbModels()"
        />
        <template #hint>
          <FieldTooltip field-name="kb_data" />
        </template>
      </UFormField>
    </div>

</template>