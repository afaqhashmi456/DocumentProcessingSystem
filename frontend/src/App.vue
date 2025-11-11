<script setup lang="ts">
import { ref } from 'vue'
import FileUpload from './components/FileUpload.vue'
import ProcessingStatus from './components/ProcessingStatus.vue'
import ResultsTable from './components/ResultsTable.vue'
import { apiClient } from './services/api'
import type { UploadStatus, ProcessResponse } from './types/document'

const files = ref<File[]>([])
const status = ref<UploadStatus>('idle')
const results = ref<ProcessResponse | null>(null)
const error = ref<string | null>(null)

// Progress tracking
const currentFile = ref<string>('')
const currentFileIndex = ref<number>(0)
const totalFiles = ref<number>(0)
const progressPercentage = ref<number>(0)

const handleFilesAdded = (newFiles: File[]) => {
  files.value = newFiles
  status.value = 'idle'
  results.value = null
  error.value = null
  resetProgress()
}

const handleClearFiles = () => {
  files.value = []
  status.value = 'idle'
  results.value = null
  error.value = null
  resetProgress()
}

const resetProgress = () => {
  currentFile.value = ''
  currentFileIndex.value = 0
  totalFiles.value = 0
  progressPercentage.value = 0
}

const handleProcessDocuments = async () => {
  if (files.value.length === 0) {
    return
  }

  try {
    status.value = 'uploading'
    error.value = null
    results.value = null
    totalFiles.value = files.value.length
    
    // Start processing with progress callbacks
    status.value = 'processing'
    
    const response = await apiClient.processDocuments(files.value, {
      onProgress: (progress) => {
        currentFile.value = progress.filename
        currentFileIndex.value = progress.current
        progressPercentage.value = progress.percentage
      },
      onError: (err) => {
        console.error('Stream error:', err)
      }
    })

    // Success
    status.value = 'completed'
    results.value = response
    
    // Clear file input
    files.value = []
    
  } catch (err) {
    status.value = 'error'
    error.value = err instanceof Error ? err.message : 'An unknown error occurred'
    console.error('Processing failed:', err)
  }
}

const isProcessing = () => status.value === 'uploading' || status.value === 'processing'
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl font-bold text-gray-900 mb-3">
          Document Processing System
        </h1>
        <p class="text-lg text-gray-600">
          OCR and AI-powered extraction for handwritten prison mail
        </p>
        <div class="mt-4 inline-flex items-center space-x-2 text-sm text-gray-500">
          <svg
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <span>Powered by Tesseract OCR & OpenAI GPT-4o-mini</span>
        </div>
      </div>

      <!-- File Upload -->
      <FileUpload
        :files="files"
        :disabled="isProcessing()"
        @files-added="handleFilesAdded"
        @clear="handleClearFiles"
      />

      <!-- Process Button -->
      <div v-if="files.length > 0" class="w-full max-w-4xl mx-auto mt-6">
        <button
          @click="handleProcessDocuments"
          :disabled="isProcessing()"
          :class="[
            'w-full py-4 px-6 rounded-lg font-semibold text-lg',
            'transition-all duration-200 shadow-lg text-white',
            isProcessing()
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700 active:bg-blue-800 hover:shadow-xl'
          ]"
        >
          <span v-if="isProcessing()" class="flex items-center justify-center">
            <svg
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
            Processing...
          </span>
          <span v-else>
            Process {{ files.length }} Document{{ files.length > 1 ? 's' : '' }}
          </span>
        </button>
      </div>

      <!-- Processing Status -->
      <ProcessingStatus
        :status="status"
        :files-count="files.length"
        :processed-count="results?.processed || 0"
        :failed-count="results?.failed || 0"
        :current-file="currentFile"
        :current-file-index="currentFileIndex"
        :total-files="totalFiles"
        :progress-percentage="progressPercentage"
      />

      <!-- Error Message -->
      <div v-if="error && status === 'error'" class="w-full max-w-4xl mx-auto mt-6">
        <div class="bg-red-50 border-2 border-red-200 rounded-lg p-6">
          <div class="flex items-start space-x-4">
            <svg
              class="h-6 w-6 text-red-600 flex-shrink-0 mt-0.5"
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
              <h3 class="text-lg font-semibold text-red-900">
                Error
              </h3>
              <p class="text-sm text-red-700 mt-1">{{ error }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Table -->
      <ResultsTable v-if="results && results.results.length > 0" :results="results.results" />

      <!-- Footer Info -->
      <div class="mt-16 text-center text-sm text-gray-500">
        <p>
          Documents are processed using Tesseract OCR (free, open-source) for text extraction
          and AI (OpenAI GPT-4o-mini) for intelligent data parsing and summarization.
        </p>
        <p class="mt-2">
          Extracted data is automatically saved to the CSV file.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import './App.css';
</style>