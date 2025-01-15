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
           <!-- {{props.pricingInfo  }} -->
            <table class="w-full text-left">
              <tbody>
               
                 <tr>
                  <td class="font-medium">Indexing Cost Estimate</td>
                  <td>{{ props?.pricingInfo?.indexing_cost_estimate ? useHumanCurrencyAmount(props?.pricingInfo?.indexing_cost_estimate) : 'Unable to fetch the data'}}</td>
                </tr>
                 <tr>
                  <td class="font-medium">Retrieval Cost Estimate</td>
                  <td>{{ props?.pricingInfo?.retrieval_cost_estimate ? useHumanCurrencyAmount(props?.pricingInfo?.retrieval_cost_estimate) : 'Unable to fetch the data'}}</td>
                </tr>
                 <tr>
                  <td class="font-medium">Evaluation Cost Estimate</td>
                  <td> {{ props?.pricingInfo?.eval_cost_estimate ? useHumanCurrencyAmount(props?.pricingInfo?.eval_cost_estimate) : 'Unable to fetch the data'}}</td>
                </tr>
              </tbody>
            </table>
          </UCard>
    </template>
  </UModal>
</template>