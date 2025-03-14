<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Fixed Header -->
    <header class="fixed top-0 left-0 right-0 bg-black shadow-[0_4px_6px_-1px_rgba(0,0,0,0.25)] z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex-shrink-0">
            <h1 class="text-2xl font-bold text-white">ImageHound</h1>
          </div>
          
          <!-- Tag Search -->
          <div class="flex-1 max-w-xl mx-4">
            <div class="relative">
              <input
                v-model="searchQuery"
                @input="handleSearch"
                @keyup.enter="performSearch"
                type="text"
                class="w-full px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-gray-800 text-white sm:border sm:border-gray-600"
                :placeholder="windowWidth >= 640 ? 'Search by tags...' : ''"
              >
              <button
                @click="performSearch"
                class="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full hover:bg-gray-700"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
              <div v-if="suggestions.length > 0" class="absolute z-10 w-full mt-1 bg-gray-800 rounded-md shadow-lg border border-gray-600">
                <ul class="py-1">
                  <li
                    v-for="suggestion in suggestions"
                    :key="suggestion"
                    @click="selectSuggestion(suggestion)"
                    class="px-4 py-2 hover:bg-gray-700 cursor-pointer text-white"
                  >
                    {{ suggestion }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Upload Button -->
          <div class="flex-shrink-0 flex items-center gap-4">
            <!-- Theme Toggle Button -->
            <button
              @click="toggleTheme"
              class="p-2 rounded-full hover:bg-gray-800"
            >
              <svg
                v-if="isDarkTheme"
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-6 w-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"
                />
              </svg>
            </button>
            <button
              @click="showUploadModal = true"
              class="p-2 rounded-full hover:bg-gray-800"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="pt-20 max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- Horizontal Album -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900">Tag Albums</h2>
          <div class="flex gap-2">
            <button
              @click="scrollAlbum('left')"
              class="p-2 rounded-full hover:bg-gray-100"
              :class="{ 'opacity-50': !canScrollLeft }"
              :disabled="!canScrollLeft"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              @click="scrollAlbum('right')"
              class="p-2 rounded-full hover:bg-gray-100"
              :class="{ 'opacity-50': !canScrollRight }"
              :disabled="!canScrollRight"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
        <div class="relative overflow-hidden">
          <div
            ref="albumContainer"
            class="flex gap-4 overflow-x-auto scrollbar-hide snap-x snap-mandatory"
          >
            <div
              v-for="album in albums"
              :key="album.tag"
              @click="selectAlbum(album.tag)"
              class="flex-shrink-0 w-64 cursor-pointer snap-center"
            >
              <div class="relative">
                <img
                  :src="album.thumbnail"
                  :alt="album.tag"
                  class="w-full h-48 object-cover rounded-lg"
                >
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white p-2 rounded-b-lg">
                  {{ album.tag }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Image Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
        <div
          v-for="image in images"
          :key="image.id"
          class="bg-white rounded-lg shadow overflow-hidden"
        >
          <img
            :src="image.url"
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
                class="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-sm tag"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Upload Modal -->
      <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-black p-8 rounded-xl max-w-md w-full shadow-2xl">
          <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Upload Image</h2>
          <div 
            class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 dark:hover:border-blue-500 transition-colors duration-200"
            @click="fileInput.click()"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p class="mt-4 text-gray-600 dark:text-gray-300 font-medium">Перетащите или добавте файл</p>
            <input
              type="file"
              ref="fileInput"
              accept="image/*"
              class="hidden"
              @change="handleFileSelect"
            >
          </div>
          <div class="mt-6 flex justify-end gap-4">
            <button
              @click="closeUploadModal"
              class="px-6 py-2 text-gray-600 dark:text-gray-300 hover:text-gray-800 dark:hover:text-white font-medium"
            >
              Отмена
            </button>
            <button
              @click="uploadImage"
              class="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 font-medium transition-colors duration-200"
            >
              Добавить
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="bg-black border-t border-gray-800/30 mt-12">
      <div class="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <!-- About Section -->
          <div class="col-span-1 md:col-span-2">
            <h3 class="text-lg font-bold text-white mb-4">About Image Gallery</h3>
            <p class="text-gray-300">
              A modern platform for sharing and organizing your photos. Upload, tag, and discover beautiful images from around the world.
            </p>
          </div>

          <!-- Quick Links -->
          <div>
            <h3 class="text-lg font-bold text-white mb-4">Quick Links</h3>
            <ul class="space-y-2">
              <li>
                <a href="#" class="text-gray-300 hover:text-white">Home</a>
              </li>
              <li>
                <a href="#" class="text-gray-300 hover:text-white">Upload</a>
              </li>
              <li>
                <a href="#" class="text-gray-300 hover:text-white">Gallery</a>
              </li>
              <li>
                <a href="#" class="text-gray-300 hover:text-white">Tags</a>
              </li>
            </ul>
          </div>

          <!-- Social Links -->
          <div>
            <h3 class="text-lg font-bold text-white mb-4">Connect With Us</h3>
            <div class="flex space-x-4">
              <a href="#" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                </svg>
              </a>
              <a href="#" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </a>
              <a href="#" class="text-gray-300 hover:text-white">
                <svg class="h-6 w-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>

        <!-- Copyright -->
        <div class="mt-8 pt-8 border-t border-gray-800">
          <p class="text-center text-gray-400">
            © {{ new Date().getFullYear() }} Image Gallery. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import axios from 'axios'

const searchQuery = ref('')
const suggestions = ref([])
const images = ref([])
const showUploadModal = ref(false)
const fileInput = ref(null)
const albumContainer = ref(null)
const albums = ref([])
const selectedTag = ref(null)
const isDarkTheme = ref(false)
const windowWidth = ref(window.innerWidth)
const canScrollLeft = ref(false)
const canScrollRight = ref(true)
const selectedFile = ref(null)

const API_BASE_URL = '/api'

// Mock data for testing
const mockAlbums = [
  {
    tag: 'All Photos',
    thumbnail: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
  },
  {
    tag: 'Nature',
    thumbnail: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
  },
  {
    tag: 'City',
    thumbnail: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
  },
  {
    tag: 'Technology',
    thumbnail: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
  },
  {
    tag: 'Food',
    thumbnail: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
  },
  {
    tag: 'Travel',
    thumbnail: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
  },
  {
    tag: 'Architecture',
    thumbnail: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
  },
  {
    tag: 'Animals',
    thumbnail: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
  },
  {
    tag: 'Art',
    thumbnail: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
  }
]

const mockImages = {
  all: [
    // Default photos
    {
      id: 1,
      filename: 'Recent Photo 1',
      tags: [{ name: 'Nature' }, { name: 'Recent' }],
      url: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
    },
    {
      id: 2,
      filename: 'Recent Photo 2',
      tags: [{ name: 'City' }, { name: 'Recent' }],
      url: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
    },
    {
      id: 3,
      filename: 'Recent Photo 3',
      tags: [{ name: 'Technology' }, { name: 'Recent' }],
      url: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
    },
    {
      id: 4,
      filename: 'Recent Photo 4',
      tags: [{ name: 'Food' }, { name: 'Recent' }],
      url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
    },
    // Nature photos
    {
      id: 5,
      filename: 'Nature Photo 1',
      tags: [{ name: 'Nature' }, { name: 'Landscape' }],
      url: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
    },
    {
      id: 6,
      filename: 'Nature Photo 2',
      tags: [{ name: 'Nature' }, { name: 'Mountains' }],
      url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop'
    },
    {
      id: 7,
      filename: 'Nature Photo 3',
      tags: [{ name: 'Nature' }, { name: 'Forest' }],
      url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop'
    },
    {
      id: 8,
      filename: 'Nature Photo 4',
      tags: [{ name: 'Nature' }, { name: 'Ocean' }],
      url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'
    },
    // City photos
    {
      id: 9,
      filename: 'City Photo 1',
      tags: [{ name: 'City' }, { name: 'Urban' }],
      url: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
    },
    {
      id: 10,
      filename: 'City Photo 2',
      tags: [{ name: 'City' }, { name: 'Architecture' }],
      url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400&h=300&fit=crop'
    },
    {
      id: 11,
      filename: 'City Photo 3',
      tags: [{ name: 'City' }, { name: 'Street' }],
      url: 'https://images.unsplash.com/photo-1449157291145-7efd050a4d0e?w=400&h=300&fit=crop'
    },
    {
      id: 12,
      filename: 'City Photo 4',
      tags: [{ name: 'City' }, { name: 'Night' }],
      url: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&h=300&fit=crop'
    },
    // Technology photos
    {
      id: 13,
      filename: 'Tech Photo 1',
      tags: [{ name: 'Technology' }, { name: 'Devices' }],
      url: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
    },
    {
      id: 14,
      filename: 'Tech Photo 2',
      tags: [{ name: 'Technology' }, { name: 'Innovation' }],
      url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop'
    },
    {
      id: 15,
      filename: 'Tech Photo 3',
      tags: [{ name: 'Technology' }, { name: 'AI' }],
      url: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop'
    },
    {
      id: 16,
      filename: 'Tech Photo 4',
      tags: [{ name: 'Technology' }, { name: 'Robotics' }],
      url: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop'
    },
    // Food photos
    {
      id: 17,
      filename: 'Food Photo 1',
      tags: [{ name: 'Food' }, { name: 'Cuisine' }],
      url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
    },
    {
      id: 18,
      filename: 'Food Photo 2',
      tags: [{ name: 'Food' }, { name: 'Restaurant' }],
      url: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop'
    },
    {
      id: 19,
      filename: 'Food Photo 3',
      tags: [{ name: 'Food' }, { name: 'Dessert' }],
      url: 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop'
    },
    {
      id: 20,
      filename: 'Food Photo 4',
      tags: [{ name: 'Food' }, { name: 'Healthy' }],
      url: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400&h=300&fit=crop'
    },
    // Travel photos
    {
      id: 21,
      filename: 'Travel Photo 1',
      tags: [{ name: 'Travel' }, { name: 'Adventure' }],
      url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
    },
    {
      id: 22,
      filename: 'Travel Photo 2',
      tags: [{ name: 'Travel' }, { name: 'Landscape' }],
      url: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=300&fit=crop'
    },
    {
      id: 23,
      filename: 'Travel Photo 3',
      tags: [{ name: 'Travel' }, { name: 'Culture' }],
      url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
    },
    {
      id: 24,
      filename: 'Travel Photo 4',
      tags: [{ name: 'Travel' }, { name: 'Beach' }],
      url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'
    },
    // Architecture photos
    {
      id: 25,
      filename: 'Architecture Photo 1',
      tags: [{ name: 'Architecture' }, { name: 'Modern' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 26,
      filename: 'Architecture Photo 2',
      tags: [{ name: 'Architecture' }, { name: 'Classical' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 27,
      filename: 'Architecture Photo 3',
      tags: [{ name: 'Architecture' }, { name: 'Interior' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 28,
      filename: 'Architecture Photo 4',
      tags: [{ name: 'Architecture' }, { name: 'Design' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    // Animals photos
    {
      id: 29,
      filename: 'Animal Photo 1',
      tags: [{ name: 'Animals' }, { name: 'Wildlife' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 30,
      filename: 'Animal Photo 2',
      tags: [{ name: 'Animals' }, { name: 'Pets' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 31,
      filename: 'Animal Photo 3',
      tags: [{ name: 'Animals' }, { name: 'Nature' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 32,
      filename: 'Animal Photo 4',
      tags: [{ name: 'Animals' }, { name: 'Birds' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    // Art photos
    {
      id: 33,
      filename: 'Art Photo 1',
      tags: [{ name: 'Art' }, { name: 'Painting' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 34,
      filename: 'Art Photo 2',
      tags: [{ name: 'Art' }, { name: 'Sculpture' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 35,
      filename: 'Art Photo 3',
      tags: [{ name: 'Art' }, { name: 'Digital' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 36,
      filename: 'Art Photo 4',
      tags: [{ name: 'Art' }, { name: 'Photography' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    }
  ],
  Nature: [
    {
      id: 5,
      filename: 'Nature Photo 1',
      tags: [{ name: 'Nature' }, { name: 'Landscape' }],
      url: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
    },
    {
      id: 6,
      filename: 'Nature Photo 2',
      tags: [{ name: 'Nature' }, { name: 'Mountains' }],
      url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop'
    },
    {
      id: 7,
      filename: 'Nature Photo 3',
      tags: [{ name: 'Nature' }, { name: 'Forest' }],
      url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop'
    },
    {
      id: 8,
      filename: 'Nature Photo 4',
      tags: [{ name: 'Nature' }, { name: 'Ocean' }],
      url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'
    }
  ],
  City: [
    {
      id: 9,
      filename: 'City Photo 1',
      tags: [{ name: 'City' }, { name: 'Urban' }],
      url: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
    },
    {
      id: 10,
      filename: 'City Photo 2',
      tags: [{ name: 'City' }, { name: 'Architecture' }],
      url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400&h=300&fit=crop'
    },
    {
      id: 11,
      filename: 'City Photo 3',
      tags: [{ name: 'City' }, { name: 'Street' }],
      url: 'https://images.unsplash.com/photo-1449157291145-7efd050a4d0e?w=400&h=300&fit=crop'
    },
    {
      id: 12,
      filename: 'City Photo 4',
      tags: [{ name: 'City' }, { name: 'Night' }],
      url: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&h=300&fit=crop'
    }
  ],
  Technology: [
    {
      id: 13,
      filename: 'Tech Photo 1',
      tags: [{ name: 'Technology' }, { name: 'Devices' }],
      url: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
    },
    {
      id: 14,
      filename: 'Tech Photo 2',
      tags: [{ name: 'Technology' }, { name: 'Innovation' }],
      url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop'
    },
    {
      id: 15,
      filename: 'Tech Photo 3',
      tags: [{ name: 'Technology' }, { name: 'AI' }],
      url: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop'
    },
    {
      id: 16,
      filename: 'Tech Photo 4',
      tags: [{ name: 'Technology' }, { name: 'Robotics' }],
      url: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop'
    }
  ],
  Food: [
    {
      id: 17,
      filename: 'Food Photo 1',
      tags: [{ name: 'Food' }, { name: 'Cuisine' }],
      url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
    },
    {
      id: 18,
      filename: 'Food Photo 2',
      tags: [{ name: 'Food' }, { name: 'Restaurant' }],
      url: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop'
    },
    {
      id: 19,
      filename: 'Food Photo 3',
      tags: [{ name: 'Food' }, { name: 'Dessert' }],
      url: 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop'
    },
    {
      id: 20,
      filename: 'Food Photo 4',
      tags: [{ name: 'Food' }, { name: 'Healthy' }],
      url: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400&h=300&fit=crop'
    }
  ],
  Travel: [
    {
      id: 21,
      filename: 'Travel Photo 1',
      tags: [{ name: 'Travel' }, { name: 'Adventure' }],
      url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
    },
    {
      id: 22,
      filename: 'Travel Photo 2',
      tags: [{ name: 'Travel' }, { name: 'Landscape' }],
      url: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=300&fit=crop'
    },
    {
      id: 23,
      filename: 'Travel Photo 3',
      tags: [{ name: 'Travel' }, { name: 'Culture' }],
      url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
    },
    {
      id: 24,
      filename: 'Travel Photo 4',
      tags: [{ name: 'Travel' }, { name: 'Beach' }],
      url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'
    }
  ],
  Architecture: [
    {
      id: 25,
      filename: 'Architecture Photo 1',
      tags: [{ name: 'Architecture' }, { name: 'Modern' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 26,
      filename: 'Architecture Photo 2',
      tags: [{ name: 'Architecture' }, { name: 'Classical' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 27,
      filename: 'Architecture Photo 3',
      tags: [{ name: 'Architecture' }, { name: 'Interior' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 28,
      filename: 'Architecture Photo 4',
      tags: [{ name: 'Architecture' }, { name: 'Design' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    }
  ],
  Animals: [
    {
      id: 29,
      filename: 'Animal Photo 1',
      tags: [{ name: 'Animals' }, { name: 'Wildlife' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 30,
      filename: 'Animal Photo 2',
      tags: [{ name: 'Animals' }, { name: 'Pets' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 31,
      filename: 'Animal Photo 3',
      tags: [{ name: 'Animals' }, { name: 'Nature' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 32,
      filename: 'Animal Photo 4',
      tags: [{ name: 'Animals' }, { name: 'Birds' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    }
  ],
  Art: [
    {
      id: 33,
      filename: 'Art Photo 1',
      tags: [{ name: 'Art' }, { name: 'Painting' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 34,
      filename: 'Art Photo 2',
      tags: [{ name: 'Art' }, { name: 'Sculpture' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 35,
      filename: 'Art Photo 3',
      tags: [{ name: 'Art' }, { name: 'Digital' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 36,
      filename: 'Art Photo 4',
      tags: [{ name: 'Art' }, { name: 'Photography' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    }
  ]
}

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
    // Simulate API call with mock data
    if (selectedTag.value === 'All Photos' || !selectedTag.value) {
      images.value = mockImages.all
    } else {
      images.value = mockImages[selectedTag.value] || []
    }
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

// Update scroll buttons visibility
const updateScrollButtons = () => {
  const container = albumContainer.value
  if (!container) return
  
  canScrollLeft.value = container.scrollLeft > 0
  canScrollRight.value = container.scrollLeft < (container.scrollWidth - container.offsetWidth - 1)
}

// Scroll album
const scrollAlbum = (direction) => {
  const container = albumContainer.value
  const albumElements = container.children
  const currentScroll = container.scrollLeft
  const containerWidth = container.offsetWidth
  const albumWidth = 256 // w-64 = 16rem = 256px
  const gap = 16 // gap-4 = 1rem = 16px
  const totalWidth = albumWidth + gap

  if (direction === 'left') {
    const targetScroll = Math.max(0, currentScroll - totalWidth)
    container.scrollTo({
      left: targetScroll,
      behavior: 'smooth'
    })
  } else {
    const targetScroll = Math.min(
      container.scrollWidth - containerWidth,
      currentScroll + totalWidth
    )
    container.scrollTo({
      left: targetScroll,
      behavior: 'smooth'
    })
  }
}

// Select album
const selectAlbum = (tag) => {
  selectedTag.value = tag
  performSearch()
}

// Fetch albums
const fetchAlbums = async () => {
  try {
    // Simulate API call with mock data
    albums.value = mockAlbums
  } catch (error) {
    console.error('Error fetching albums:', error)
  }
}

// Handle file selection
const handleFileSelect = (event) => {
  selectedFile.value = event.target.files[0]
}

// Handle drag and drop
const handleDrop = (event) => {
  const file = event.dataTransfer.files[0]
  if (file && file.type.startsWith('image/')) {
    selectedFile.value = file
    fileInput.value.files = event.dataTransfer.files
  }
}

// Close upload modal
const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Update upload image function
const uploadImage = async () => {
  const file = selectedFile.value || fileInput.value.files[0]
  if (!file) {
    alert('Please select an image first')
    return
  }

  const formData = new FormData()
  formData.append('file', file)

  try {
    // For demo purposes, we'll simulate a successful upload
    console.log('Uploading file:', file.name)
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulate API delay
    
    // Add the new image to the mock data
    const newImage = {
      id: mockImages.all.length + 1,
      filename: file.name,
      tags: [{ name: 'New' }],
      url: URL.createObjectURL(file)
    }
    
    mockImages.all.unshift(newImage)
    mockImages['New'] = [newImage]
    
    // Update the UI
    images.value = mockImages.all
    closeUploadModal()
    alert('Image uploaded successfully!')
  } catch (error) {
    console.error('Error uploading image:', error)
    alert('Error uploading image. Please try again.')
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

// Theme functions
const toggleTheme = () => {
  isDarkTheme.value = !isDarkTheme.value
  updateTheme()
}

const updateTheme = () => {
  if (isDarkTheme.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
  localStorage.setItem('theme', isDarkTheme.value ? 'dark' : 'light')
}

// Initialize theme from localStorage
const initTheme = () => {
  const savedTheme = localStorage.getItem('theme')
  isDarkTheme.value = savedTheme === 'dark'
  updateTheme()
}

// Watch for system theme changes
const watchSystemTheme = () => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleChange = (e) => {
    isDarkTheme.value = e.matches
    updateTheme()
  }
  mediaQuery.addEventListener('change', handleChange)
}

// Add window resize handler
const handleResize = () => {
  windowWidth.value = window.innerWidth
}

// Initial load
onMounted(() => {
  initTheme()
  watchSystemTheme()
  fetchAlbums()
  performSearch()
  window.addEventListener('resize', handleResize)
  
  // Add scroll event listener to update button visibility
  if (albumContainer.value) {
    albumContainer.value.addEventListener('scroll', updateScrollButtons)
  }
})

// Clean up event listener
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (albumContainer.value) {
    albumContainer.value.removeEventListener('scroll', updateScrollButtons)
  }
})
</script>

<style>
/* Import Inter Black, Regular, and Medium fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;900&display=swap');

/* Apply Inter Black font to all elements */
* {
  font-family: 'Inter', sans-serif;
  font-weight: 900;
}

/* Apply Inter Regular font to tags */
.tag {
  font-weight: 400;
}

/* Apply Inter Medium font to modal elements */
.modal-content {
  font-weight: 500;
}

.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Add smooth scrolling behavior */
.snap-x {
  scroll-behavior: smooth;
}

/* Dark theme styles */
.dark {
  color-scheme: dark;
}

.dark body {
  @apply text-gray-100;
  background-color: #212020;
}

.dark .bg-white {
  @apply bg-gray-800;
}

.dark .text-gray-900 {
  @apply text-gray-100;
}

.dark .border-gray-300 {
  @apply border-gray-600;
}

.dark .bg-gray-100 {
  background-color: #212020;
}

.dark .shadow {
  @apply shadow-gray-900;
}

.dark .bg-blue-100 {
  @apply bg-blue-900;
}

.dark .text-blue-800 {
  @apply text-blue-100;
}

.dark .hover\:bg-gray-100:hover {
  @apply hover:bg-gray-700;
}

.dark .hover\:text-gray-800:hover {
  @apply hover:text-gray-200;
}

.dark .bg-black.bg-opacity-50 {
  @apply bg-opacity-75;
}

.dark .text-gray-600 {
  @apply text-gray-300;
}

/* Update header background in dark mode */
.dark header {
  background-color: #212020;
}

/* Update modal background in dark mode */
.dark .bg-white.dark\:bg-black {
  background-color: #000000 !important;
}

.bg-white {
  background-color: #f2f1f1 !important;
}

/* Update input background in dark mode */
.dark input {
  background-color: #212020;
  border-color: #4a4a4a;
  color: #f2f1f1;
}

.dark input::placeholder {
  color: #9ca3af;
}

/* Update suggestions dropdown in dark mode */
.dark .bg-white.rounded-md {
  background-color: #212020;
  border: 1px solid #4a4a4a;
}

.dark .hover\:bg-gray-100:hover {
  background-color: #2d2d2d;
}

/* Update image card background in dark mode */
.dark .bg-white.rounded-lg {
  background-color: #282828;
}

/* Update tag background in both themes */
.bg-blue-100 {
  background-color: rgba(219, 234, 254, 0.65) !important;
  color: #1e40af !important;
}

.dark .bg-blue-100 {
  background-color: rgba(112, 52, 210, 0.65) !important;
  color: #f2f1f1 !important;
}
</style> 