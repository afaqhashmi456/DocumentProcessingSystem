<script setup lang="ts">
import { ref } from 'vue'
import type { FileProcessResult } from '../types/document'
import DownloadButton from './DownloadButton.vue'

interface Props {
  results: FileProcessResult[]
}

defineProps<Props>()

const expandedRows = ref<Set<number>>(new Set())

const toggleRow = (index: number) => {
  if (expandedRows.value.has(index)) {
    expandedRows.value.delete(index)
  } else {
    expandedRows.value.add(index)
  }
}

const truncateText = (text: string, maxLength: number = 100): string => {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<template>
  <div v-if="results.length > 0" class="w-full max-w-6xl mx-auto mt-8">
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <h2 class="text-xl font-bold text-gray-800">
          Extraction Results
        </h2>
        <p class="text-sm text-gray-600 mt-1">
          {{ results.length }} document(s) processed
        </p>
      </div>

      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Filename
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                DOC #
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Facility
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Summary
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <template v-for="(result, index) in results" :key="index">
              <tr class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {{ result.filename }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  <div v-if="result.success && result.data">
                    <div class="font-medium">
                      {{ result.data.first_name }} {{ result.data.middle_name || '' }} {{ result.data.last_name }}
                    </div>
                  </div>
                  <span v-else class="text-gray-400">N/A</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                  {{ result.success && result.data ? result.data.doc_number : 'N/A' }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-700">
                  <div v-if="result.success && result.data" class="max-w-xs">
                    <div class="font-medium">{{ result.data.facility_name }}</div>
                    <div v-if="result.data.unit" class="text-xs text-gray-500">Unit: {{ result.data.unit }}</div>
                  </div>
                  <span v-else>N/A</span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-700">
                  <div v-if="result.success && result.data" class="max-w-md">
                    {{ truncateText(result.data.ai_summary, 80) }}
                  </div>
                  <span v-else>N/A</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    v-if="result.success"
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                  >
                    Success
                  </span>
                  <span
                    v-else
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800"
                  >
                    Failed
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    v-if="result.success && result.data"
                    @click="toggleRow(index)"
                    class="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {{ expandedRows.has(index) ? 'Hide' : 'Show' }} Details
                  </button>
                </td>
              </tr>

              <tr v-if="expandedRows.has(index) && result.success && result.data" :key="`${index}-expanded`">
                <td colspan="7" class="px-6 py-4 bg-gray-50">
                  <div class="space-y-4">
                    <div class="grid grid-cols-2 gap-4">
                      <div>
                        <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">
                          Personal Information
                        </h4>
                        <dl class="space-y-1">
                          <div class="flex justify-between">
                            <dt class="text-sm text-gray-600">Full Name:</dt>
                            <dd class="text-sm font-medium text-gray-900">
                              {{ result.data.first_name }} {{ result.data.middle_name || '' }} {{ result.data.last_name }}
                            </dd>
                          </div>
                          <div class="flex justify-between">
                            <dt class="text-sm text-gray-600">DOC Number:</dt>
                            <dd class="text-sm font-medium text-gray-900">
                              {{ result.data.doc_number }}
                            </dd>
                          </div>
                          <div class="flex justify-between">
                            <dt class="text-sm text-gray-600">Date Processed:</dt>
                            <dd class="text-sm font-medium text-gray-900">
                              {{ result.data.date_created }}
                            </dd>
                          </div>
                        </dl>
                      </div>

                      <div>
                        <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">
                          Facility Information
                        </h4>
                        <dl class="space-y-1">
                          <div class="flex justify-between">
                            <dt class="text-sm text-gray-600">Facility:</dt>
                            <dd class="text-sm font-medium text-gray-900">
                              {{ result.data.facility_name }}
                            </dd>
                          </div>
                          <div class="flex justify-between">
                            <dt class="text-sm text-gray-600">Address:</dt>
                            <dd class="text-sm font-medium text-gray-900 text-right">
                              {{ result.data.address }}
                            </dd>
                          </div>
                          <div v-if="result.data.unit" class="flex justify-between">
                            <dt class="text-sm text-gray-600">Unit:</dt>
                            <dd class="text-sm font-medium text-gray-900">
                              {{ result.data.unit }}
                            </dd>
                          </div>
                        </dl>
                      </div>
                    </div>

                    <div>
                      <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">
                        AI Summary
                      </h4>
                      <p class="text-sm text-gray-700 bg-white p-3 rounded border border-gray-200">
                        {{ result.data.ai_summary }}
                      </p>
                    </div>

                    <div>
                      <h4 class="text-xs font-semibold text-gray-500 uppercase mb-2">
                        Raw Extracted Text
                      </h4>
                      <div class="bg-white p-3 rounded border border-gray-200 max-h-48 overflow-y-auto">
                        <pre class="text-xs text-gray-700 whitespace-pre-wrap font-mono">{{ result.data.raw_text }}</pre>
                      </div>
                    </div>

                    <div v-if="result.processing_time" class="text-xs text-gray-500 text-right">
                      Processing time: {{ result.processing_time.toFixed(2) }}s
                    </div>
                  </div>
                </td>
              </tr>

              <tr v-if="!result.success && result.error" :key="`${index}-error`">
                <td colspan="7" class="px-6 py-4 bg-red-50">
                  <div class="flex items-start space-x-2">
                    <svg
                      class="h-5 w-5 text-red-500 mt-0.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <div>
                      <p class="text-sm font-medium text-red-900">Error Details:</p>
                      <p class="text-sm text-red-700 mt-1">{{ result.error }}</p>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <DownloadButton :results="results" />
    </div>
  </div>
</template>