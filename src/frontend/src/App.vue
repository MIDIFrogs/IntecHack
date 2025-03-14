<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold text-gray-900">Image Search</h1>
      </div>
    </header>

    <main class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- Search Bar -->
      <div class="mb-8">
        <div class="relative">
          <input
            v-model="searchQuery"
            @input="handleSearch"
            @keyup.enter="performSearch"
            type="text"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Search images..."
          >
          <div v-if="suggestions.length > 0" class="absolute z-10 w-full mt-1 bg-white rounded-md shadow-lg">
            <ul class="py-1">
              <li
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="selectSuggestion(suggestion)"
                class="px-4 py-2 hover:bg-gray-100 cursor-pointer"
              >
                {{ suggestion }}
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Upload Button -->
      <div class="mb-8">
        <button
          @click="showUploadModal = true"
          class="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
        >
          Upload Image
        </button>
      </div>

      <!-- Image Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div
          v-for="image in images"
          :key="image.id"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <img
            :src="`/api/images/${image.id}`"
            :alt="image.filename"
            class="w-full h-48 object-cover cursor-pointer"
            @click="downloadImage(image.id)"
          >
          <div class="p-4">
            <h3 class="text-lg font-semibold mb-2">{{ image.filename }}</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in image.tags"
                :key="tag.name"
                class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Modal -->
      <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div class="bg-white p-6 rounded-lg max-w-md w-full">
          <h2 class="text-xl font-bold mb-4">Upload Image</h2>
          <input
            type="file"
            ref="fileInput"
            accept="image/*"
            class="mb-4"
          >
          <div class="flex justify-end gap-4">
            <button
              @click="showUploadModal = false"
              class="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              @click="uploadImage"
              class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
            >
              Upload
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const suggestions = ref([])
const images = ref([])
const showUploadModal = ref(false)
const fileInput = ref(null)

const API_BASE_URL = '/api'

// Debounce function
const debounce = (fn, delay) => {
  let timeoutId
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn(...args), delay)
  }
}

// Handle search input
const handleSearch = debounce(async () => {
  if (searchQuery.value.length < 2) {
    suggestions.value = []
    return
  }
  
  try {
    const response = await axios.get(`${API_BASE_URL}/suggestions`, {
      params: { q: searchQuery.value }
    })
    suggestions.value = response.data
  } catch (error) {
    console.error('Error fetching suggestions:', error)
  }
}, 300)

// Perform search
const performSearch = async () => {
  suggestions.value = []
  try {
    const response = await axios.get(`${API_BASE_URL}/images`, {
      params: { q: searchQuery.value }
    })
    images.value = response.data.images
  } catch (error) {
    console.error('Error searching images:', error)
  }
}

// Select suggestion
const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion
  suggestions.value = []
  performSearch()
}

// Upload image
const uploadImage = async () => {
  const file = fileInput.value.files[0]
  if (!file) return

  const formData = new FormData()
  formData.append('file', file)

  try {
    await axios.post(`${API_BASE_URL}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    showUploadModal.value = false
    performSearch()
  } catch (error) {
    console.error('Error uploading image:', error)
  }
}

// Download image
const downloadImage = async (imageId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/images/${imageId}`, {
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'image.jpg')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Error downloading image:', error)
  }
}

// Initial load
onMounted(() => {
  performSearch()
})
</script> 