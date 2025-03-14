<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Fixed Header -->
    <header class="fixed top-0 left-0 right-0 bg-white shadow-md z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex-shrink-0">
            <h1 class="text-2xl font-bold text-gray-900">Image Gallery</h1>
          </div>

          <!-- Search Bar -->
          <div class="flex-1 max-w-2xl mx-4">
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="handleSearch"
                @keyup.enter="performSearch"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Search by tags..."
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
          <div class="flex-shrink-0">
            <button
              @click="showUploadModal = true"
              class="p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="pt-20 pb-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Horizontal Album -->
        <div class="mb-8">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900">Featured Albums</h2>
            <div class="flex space-x-2">
              <button
                @click="scrollAlbum('left')"
                class="p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <button
                @click="scrollAlbum('right')"
                class="p-2 text-gray-600 hover:text-gray-900 focus:outline-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
          <div
            ref="albumContainer"
            class="flex overflow-x-auto space-x-4 pb-4 scrollbar-hide"
          >
            <div
              v-for="album in albums"
              :key="album.id"
              class="flex-shrink-0 w-64 cursor-pointer"
              @click="loadAlbumImages(album.tag)"
            >
              <div class="relative">
                <img
                  :src="album.thumbnail"
                  :alt="album.name"
                  class="w-full h-48 object-cover rounded-lg"
                >
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 rounded-b-lg">
                  {{ album.name }}
                </div>
              </div>
            </div>
          </div>
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
      </div>
    </main>

    <!-- Upload Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// State variables
const searchQuery = ref('')
const suggestions = ref([])
const images = ref([])
const showUploadModal = ref(false)
const fileInput = ref(null)
const albumContainer = ref(null)
const albums = ref([
  { id: 1, name: 'Nature', tag: 'nature', thumbnail: '/sample/nature.jpg' },
  { id: 2, name: 'City', tag: 'city', thumbnail: '/sample/city.jpg' },
  { id: 3, name: 'People', tag: 'people', thumbnail: '/sample/people.jpg' },
  { id: 4, name: 'Technology', tag: 'technology', thumbnail: '/sample/tech.jpg' },
])

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

// Load album images
const loadAlbumImages = async (tag) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/images`, {
      params: { tag }
    })
    images.value = response.data.images
  } catch (error) {
    console.error('Error loading album images:', error)
  }
}

// Scroll album
const scrollAlbum = (direction) => {
  const container = albumContainer.value
  const scrollAmount = 300
  if (direction === 'left') {
    container.scrollLeft -= scrollAmount
  } else {
    container.scrollLeft += scrollAmount
  }
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
    loadRecentImages()
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

// Load recent images
const loadRecentImages = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/images`, {
      params: { sort: 'recent' }
    })
    images.value = response.data.images
  } catch (error) {
    console.error('Error loading recent images:', error)
  }
}

// Initial load
onMounted(() => {
  loadRecentImages()
})
</script>

<style>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style> 