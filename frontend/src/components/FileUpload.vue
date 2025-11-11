<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  files: File[]
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false
})

const emit = defineEmits<{
  filesAdded: [files: File[]]
  clear: []
}>()

const isDragActive = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)

const onDragEnter = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  if (!props.disabled) {
    isDragActive.value = true
  }
}

const onDragLeave = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isDragActive.value = false
}

const onDragOver = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
}

const onDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  isDragActive.value = false
  
  if (props.disabled) return

  const droppedFiles = Array.from(e.dataTransfer?.files || [])
  const pdfFiles = droppedFiles.filter(file => file.type === 'application/pdf')
  
  if (pdfFiles.length > 0) {
    emit('filesAdded', pdfFiles)
  }
}

const onClick = () => {
  if (!props.disabled && fileInput.value) {
    fileInput.value.click()
  }
}

const onFileInputChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const selectedFiles = Array.from(target.files)
    emit('filesAdded', selectedFiles)
    // Reset input so same file can be selected again
    target.value = ''
  }
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const totalSize = () => props.files.reduce((sum, file) => sum + file.size, 0)
</script>

<template>
  <div class="w-full max-w-4xl mx-auto">
    <div
      @dragenter="onDragEnter"
      @dragleave="onDragLeave"
      @dragover="onDragOver"
      @drop="onDrop"
      @click="onClick"
      :class="[
        'border-2 border-dashed rounded-lg p-12 text-center cursor-pointer',
        'transition-all duration-200',
        isDragActive
          ? 'border-blue-500 bg-blue-50'
          : 'border-gray-300 hover:border-gray-400 bg-white',
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      ]"
    >
      <input
        ref="fileInput"
        type="file"
        accept="application/pdf"
        multiple
        @change="onFileInputChange"
        style="display: none"
      />
      
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        stroke="currentColor"
        fill="none"
        viewBox="0 0 48 48"
        aria-hidden="true"
      >
        <path
          d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>

      <div class="mt-4">
        <p v-if="isDragActive" class="text-lg text-blue-600 font-medium">
          Drop the files here...
        </p>
        <template v-else>
          <p class="text-lg text-gray-700 font-medium">
            Drag & drop PDF files here
          </p>
          <p class="text-sm text-gray-500 mt-1">
            or click to select files
          </p>
        </template>
      </div>

      <p class="text-xs text-gray-400 mt-2">
        PDF files only, up to 10MB each
      </p>
    </div>

    <div v-if="files.length > 0" class="mt-6 bg-white rounded-lg shadow p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-800">
          Selected Files ({{ files.length }})
        </h3>
        <button
          @click.stop="emit('clear')"
          :disabled="disabled"
          class="text-sm text-red-600 hover:text-red-700 font-medium disabled:opacity-50"
        >
          Clear All
        </button>
      </div>

      <div class="space-y-2 max-h-64 overflow-y-auto">
        <div
          v-for="(file, index) in files"
          :key="`${file.name}-${index}`"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <div class="flex items-center space-x-3 flex-1 min-w-0">
            <svg
              class="h-8 w-8 text-red-500 flex-shrink-0"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fill-rule="evenodd"
                d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"
                clip-rule="evenodd"
              />
            </svg>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 truncate">
                {{ file.name }}
              </p>
              <p class="text-xs text-gray-500">
                {{ formatFileSize(file.size) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="mt-4 pt-4 border-t border-gray-200">
        <div class="flex justify-between text-sm">
          <span class="text-gray-600">Total size:</span>
          <span class="font-semibold text-gray-900">
            {{ formatFileSize(totalSize()) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>