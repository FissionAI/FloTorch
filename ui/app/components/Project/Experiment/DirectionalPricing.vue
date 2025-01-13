<script setup lang="ts">

    const props = defineProps<{
    label : string
    price : string
    pricingInfo : any
    }>()
    
    const isOpen = ref(false)

</script>


<template>
  <a href="#" class="text-blue-500 hover:underline" @click.prevent="isOpen = true">{{props.price}}</a>
  <UModal class="overflow-y-scroll max-h-[50vh]" v-model:open="isOpen" :title="props.label">
    <template #body>
        <UCard>
           
            <table class="w-full text-left">
              <tbody>
                <tr>
                  <td class="font-medium">Eval Cost Estimate</td>
                  <td>{{useHumanCurrencyAmount(props?.pricingInfo?.eval_cost_estimate)}}</td>
                </tr>
                 <tr>
                  <td class="font-medium">Index Cost Estimate</td>
                  <td>{{useHumanCurrencyAmount(props?.pricingInfo?.indexing_cost_estimate)}}</td>
                </tr>
                 <tr>
                  <td class="font-medium">Retrieval Cost Estimate</td>
                  <td>{{useHumanCurrencyAmount(props?.pricingInfo?.retrieval_cost_estimate)}}</td>
                </tr>
              </tbody>
            </table>
          </UCard>
    </template>
  </UModal>
</template>