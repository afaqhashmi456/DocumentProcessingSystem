<script setup lang="ts">
import { ref } from 'vue'
import type { FileProcessResult } from '../types/document'
import { downloadCSV, downloadExcel } from '../utils/downloadUtils'

interface Props {
  results: FileProcessResult[]
}

defineProps<Props>()

type ExportFormat = 'csv' | 'excel'

const format = ref<ExportFormat>('excel')
const isDownloading = ref(false)

const handleDownload = async (results: FileProcessResult[]) => {
  if (results.length === 0) return

  isDownloading.value = true
  try {
    const timestamp = new Date().toISOString().split('T')[0]
    const filename = `extracted-data-${timestamp}`

    if (format.value === 'csv') {
      downloadCSV(results, `${filename}.csv`)
    } else {
      await downloadExcel(results, `${filename}.xlsx`)
    }
  } catch (error) {
    console.error('Download failed:', error)
    alert('Failed to download file. Please try again.')
  } finally {
    isDownloading.value = false
  }
}
</script>

<template>
  <div v-if="results.length > 0" class="flex items-center justify-end gap-3 px-6 py-4 bg-gray-50 border-t border-gray-200">
    <label for="format-select" class="text-sm font-medium text-gray-700">
      Download as:
    </label>
    
    <select
      id="format-select"
      v-model="format"
      class="block rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm py-2 px-3 pr-10"
      :disabled="isDownloading"
    >
      <option value="excel">Excel (.xlsx)</option>
      <option value="csv">CSV (.csv)</option>
    </select>

    <button
      @click="handleDownload(results)"
      :disabled="isDownloading"
      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
      <template v-if="isDownloading">
        <svg
          class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          />
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
        Downloading...
      </template>
      <template v-else>
        <svg
          class="-ml-1 mr-2 h-4 w-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
        Download Results
      </template>
    </button>
  </div>
</template>