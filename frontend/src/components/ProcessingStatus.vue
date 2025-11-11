<script setup lang="ts">
import type { UploadStatus } from '../types/document'

interface Props {
  status: UploadStatus
  filesCount?: number
  processedCount?: number
  failedCount?: number
  currentFile?: string
  currentFileIndex?: number
  totalFiles?: number
  progressPercentage?: number
}

withDefaults(defineProps<Props>(), {
  filesCount: 0,
  processedCount: 0,
  failedCount: 0,
  currentFile: '',
  currentFileIndex: 0,
  totalFiles: 0,
  progressPercentage: 0
})
</script>

<template>
  <div v-if="status !== 'idle'" class="w-full max-w-4xl mx-auto mt-6">
    <div
      :class="[
        'rounded-lg p-6 shadow-lg',
        (status === 'uploading' || status === 'processing') ? 'bg-blue-50 border-2 border-blue-200' : '',
        status === 'completed' ? 'bg-green-50 border-2 border-green-200' : '',
        status === 'error' ? 'bg-red-50 border-2 border-red-200' : ''
      ]"
    >
      <div v-if="status === 'uploading' || status === 'processing'" class="flex items-center space-x-4">
        <div class="flex-shrink-0">
          <svg
            class="animate-spin h-8 w-8 text-blue-600"
            xmlns="http://www.w3.org/2000/svg"
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
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-blue-900">
            {{ status === 'uploading' ? 'Uploading Files...' : 'Processing Documents...' }}
          </h3>
          <p class="text-sm text-blue-700 mt-1">
            {{ status === 'uploading'
              ? 'Sending files to server...'
              : 'Extracting text with OCR and AI analysis. This may take a few minutes...' }}
          </p>

          <div v-if="status === 'processing' && totalFiles > 0" class="mt-3">
            <div class="flex justify-between text-sm text-blue-800 mb-2">
              <span class="font-medium">
                Processing file {{ currentFileIndex }} of {{ totalFiles }}
              </span>
              <span class="font-semibold">{{ progressPercentage }}%</span>
            </div>
            
            <div v-if="currentFile" class="text-xs text-blue-700 mb-2 truncate">
              📄 {{ currentFile }}
            </div>
            
            <div class="w-full bg-blue-200 rounded-full h-3 overflow-hidden">
              <div
                class="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
                :style="{ width: `${progressPercentage}%` }"
              />
            </div>
          </div>
          
          <div v-else-if="filesCount > 0" class="mt-3">
            <div class="flex justify-between text-sm text-blue-800 mb-1">
              <span>Processing {{ filesCount }} document(s)</span>
            </div>
            <div class="w-full bg-blue-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full animate-pulse"
                style="width: 60%"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="status === 'completed'" class="flex items-start space-x-4">
        <div class="flex-shrink-0">
          <svg
            class="h-8 w-8 text-green-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-green-900">
            Processing Complete!
          </h3>
          <div class="mt-2 space-y-1">
            <p class="text-sm text-green-800">
              <span class="font-semibold">{{ processedCount }}</span> document(s) processed successfully
            </p>
            <p v-if="failedCount > 0" class="text-sm text-red-700">
              <span class="font-semibold">{{ failedCount }}</span> document(s) failed
            </p>
          </div>
          <p class="text-xs text-green-700 mt-2">
            Data has been saved to the CSV file.
          </p>
        </div>
      </div>

      <div v-else-if="status === 'error'" class="flex items-start space-x-4">
        <div class="flex-shrink-0">
          <svg
            class="h-8 w-8 text-red-600"
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
        </div>
        <div class="flex-1">
          <h3 class="text-lg font-semibold text-red-900">
            Processing Failed
          </h3>
          <p class="text-sm text-red-700 mt-1">
            An error occurred while processing the documents. Please check the files and try again.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>