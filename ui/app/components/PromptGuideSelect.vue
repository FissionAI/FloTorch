<script setup lang="ts">
import type { FormError } from '@nuxt/ui';
import { z } from 'zod'
const modelValue = defineModel<ProjectNShotPromptGuide>()
const props = defineProps<{
  requiredPrompts: number
}>()

const { open, reset, onChange } = useFileDialog({
  accept: "application/json",
  directory: false,
})

const validationSchema = computed(() => {
  const schema = ProjectNShotPromptGuideSchema.extend({
    examples: z.array(z.object({
          example: z.string(),
        })).min(props.requiredPrompts, {
        message: `Must have at least ${props.requiredPrompts} examples`
      })
  })
  if (props.requiredPrompts > 0) {
    return schema
  }
  return schema.optional()
})

const emits = defineEmits<{
  error: [FormError | undefined]
}>()

onChange(async (files) => {
  if (!files || files.length === 0) {
    return
  }
  const file = files[0]
  const reader = new FileReader()
  reader.onload = (e) => {
    let errorMessage:string = ''
    try {
      const json = JSON.parse(e.target?.result as string)
      if(!json['user_prompt'] || !json['system_prompt']){
        errorMessage = "User prompt and System prompt are required in json file."
      }else {
        errorMessage = ''
      }
      const parsed = validationSchema.value.safeParse(json)
      if (parsed.success) {
        modelValue.value = parsed.data
        filepath.value = "Attached"
        emits("error", undefined)
      } else {
        const errorMsg = errorMessage || "Upload a valid json file"
        emits("error", { name: "n_shot_prompt_guide", message: errorMsg });
      }
    } catch (error) {
      console.error(error);
      emits("error", {
        name: "n_shot_prompt_guide",
        message: "Invalid file format",
      });
       modelValue.value = undefined;
    } finally {
      reset();
    }
  };
  reader.readAsText(file!, "UTF-8");
})

const handleOpen = ()=>{
  reset();
  modelValue.value = undefined;
  open();
}

const filepath = ref('')
const isUploading = ref(false)
</script>

<template>
  <UButtonGroup class="w-full">
    <UInput :value="modelValue !== undefined ? 'Attached' : ''" v-model="filepath" disabled />
    <UButton class="secondary-btn ml-2" leading-icon="i-lucide-arrow-up-to-line" label="Choose File" variant="ghost" :loading="isUploading" @click="handleOpen()" />
  </UButtonGroup>
</template>
