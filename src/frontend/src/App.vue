<template>
  <div class="min-h-screen">
    <!-- Fixed Header -->
    <header class="fixed top-0 left-0 right-0 bg-header shadow-[0_4px_6px_-1px_rgba(0,0,0,0.25)] z-50">
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
                ref="searchInput"
                v-model="searchQuery"
                @input="handleSearch"
                @keyup.enter="performSearch"
                type="text"
                class="w-full px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-search text-white sm:border sm:border-gray-600"
                :placeholder="windowWidth >= 640 ? 'Поиск по тегам...' : ''"
              >
              <button
                @click="() => { focusSearch(); performSearch(); }"
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
          <h2 class="text-xl font-semibold text-gray-900">Альбомы тегов</h2>
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
            <h3 class="text-lg font-medium mb-2">{{ image.filename }}</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in image.tags"
                :key="tag.name"
                class="px-2 py-1 tag-bg rounded-full text-sm tag"
              >
                {{ tag.name }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Add loading indicator and observer target -->
      <div 
        v-if="hasMoreImages" 
        ref="observerTarget"
        class="flex justify-center items-center py-8"
      >
        <div v-if="loadingMore" class="flex items-center justify-center">
          <div class="loading-spinner"></div>
        </div>
      </div>
      
      <!-- Upload Modal -->
      <div
        v-if="showUploadModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click="closeUploadModal"
      >
        <div
          class="bg-white p-8 rounded-xl max-w-md w-full shadow-2xl max-h-[80vh] flex flex-col"
          @click.stop
        >
          <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">Загрузить</h2>
          <div 
            v-if="!selectedFiles.length"
            class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 dark:hover:border-[#7034d2a6] transition-colors duration-200 flex-1"
            @click="fileInput.click()"
            @dragover.prevent
            @drop.prevent="handleDrop"
          >
            <div class="flex flex-col items-center justify-center h-full">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="mt-4 text-gray-600 dark:text-gray-300 font-medium">Перетащите или добавьте файлы</p>
              <input
                type="file"
                ref="fileInput"
                accept="image/*"
                multiple
                class="hidden"
                @change="handleFileSelect"
              >
            </div>
          </div>
          <div 
            v-else
            class="flex-1 flex flex-col min-h-0"
          >
            <div class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-4 overflow-y-auto flex-1">
              <div class="space-y-4">
                <div v-for="(file, index) in selectedFiles" :key="index" class="relative">
                  <div class="flex items-center gap-4 mb-2">
                    <img
                      :src="previewUrls[index]"
                      alt="Preview"
                      class="h-16 w-16 object-cover rounded"
                    >
                    <div class="flex-1 min-w-0">
                      <p 
                        class="text-sm font-medium truncate" 
                        :title="file.name"
                      >
                        {{ file.name.length > 25 ? file.name.substring(0, 25) + '...' : file.name }}
                      </p>
                      <div v-if="uploadProgress[index] !== undefined" class="w-full h-2 bg-gray-200 rounded-full mt-2">
                        <div 
                          class="h-full tag-bg rounded-full transition-all duration-300"
                          :style="{ width: `${uploadProgress[index]}%` }"
                        ></div>
                      </div>
                    </div>
                    <button
                      @click="removeFile(index)"
                      class="p-1 rounded-full bg-gray-800 bg-opacity-50 hover:bg-opacity-70 transition-opacity flex-shrink-0"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-4">
            <button
              @click="closeUploadModal"
              class="px-6 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-100 font-medium transition-colors duration-200"
            >
              Отмена
            </button>
            <button
              @click="uploadImages"
              :disabled="isUploading"
              class="px-6 py-2 tag-bg rounded-lg font-medium transition-colors duration-200 dark:tag-bg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {{ isUploading ? 'Загрузка...' : 'Добавить' }}
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer-gradient border-t border-gray-800/30 mt-12">
      <div class="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-5 gap-12">
          <!-- About Section -->
          <div class="col-span-1 md:col-span-3 space-y-6">
            <div class="flex items-center gap-3">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <h3 class="text-2xl font-bold text-white">ImageHound</h3>
            </div>
            <p class="text-gray-300 text-lg leading-relaxed">
              Современная платформа для обмена и организации ваших фотографий. Загружайте, отмечайте тегами и открывайте для себя прекрасные изображения со всего мира. Присоединяйтесь к нашему сообществу фотографов и ценителей искусства.
            </p>
            <p class="text-gray-400">
              © {{ new Date().getFullYear() }} ImageHound. Все права защищены.
            </p>
          </div>

          <!-- Navigation Links -->
          <div class="space-y-4">
            <ul class="space-y-4">
              <li>
                <a href="#" class="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                  </svg>
                  Главная
                </a>
              </li>
              <li>
                <button
                  @click="showUploadModal = true"
                  class="text-gray-300 hover:text-white transition-colors duration-200 flex items-center gap-2"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                  Загрузить
                </button>
              </li>
            </ul>
          </div>

          <!-- Quick Links and Social Media -->
          <div class="space-y-8">
            <h3 class="text-xl font-bold text-white mb-6">Быстрые ссылки</h3>
            <div class="flex items-center gap-6">
              <a href="#" class="text-gray-300 hover:text-white transition-colors duration-200">
                <svg class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.237 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
                </svg>
              </a>
              <a href="#" class="text-gray-300 hover:text-white transition-colors duration-200">
                <svg class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M15.684 0H8.316C1.592 0 0 1.592 0 8.316v7.368C0 22.408 1.592 24 8.316 24h7.368C22.408 24 24 22.408 24 15.684V8.316C24 1.592 22.408 0 15.684 0zm3.692 17h-1.372c-.538 0-.691-.447-1.666-1.422-1.023-1.023-1.503-1.193-1.768-1.193-.36.008-.411.254-.411.619v1.297c0 .34-.134.539-1.117.539-1.244.043-2.427-.105-3.438-.831a11.159 11.159 0 01-3.086-3.348c-1.593-2.329-2.228-4.146-2.228-4.528 0-.188.082-.366.537-.366h1.645c.39 0 .537.172.691.573.768 2.204 2.043 4.129 2.563 4.129.195 0 .283-.089.283-.573v-2.329c-.06-1.027-.602-1.112-.602-1.476 0-.172.142-.344.369-.344h2.563c.351 0 .46.172.46.573v3.149c0 .337.142.46.23.46.195 0 .351-.123.703-.475.999-1.115 1.707-2.83 1.707-2.83.09-.197.254-.38.644-.38h1.645c.499 0 .602.254.499.573-.207.96-2.254 3.859-2.254 3.859-.172.287-.23.41 0 .722.172.254.723.779 1.092 1.25.681.85 1.201 1.562 1.35 2.062.135.466-.101.703-.57.703z"/>
                </svg>
              </a>
              <a href="#" class="text-gray-300 hover:text-white transition-colors duration-200">
                <svg class="h-8 w-8" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18 1.897-.962 6.502-1.359 8.627-.168.9-.5 1.201-.82 1.23-.697.064-1.226-.461-1.901-.903-1.056-.692-1.653-1.123-2.678-1.799-1.185-.781-.417-1.21.258-1.911.177-.184 3.247-2.977 3.307-3.23.007-.032.015-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.139-5.062 3.345-.479.329-.913.489-1.302.481-.428-.009-1.252-.242-1.865-.44-.751-.245-1.349-.374-1.297-.789.027-.216.324-.437.893-.663 3.498-1.524 5.831-2.529 6.998-3.015 3.333-1.386 4.025-1.627 4.477-1.635.099-.002.321.023.465.137.12.095.145.219.137.342l-.002.001z"/>
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
    <!-- Anchor Button -->
    <button
      v-show="showAnchor"
      @click="scrollToTop"
      class="fixed bottom-8 right-8 p-3 rounded-full bg-gray-800 dark:bg-gray-700 text-white shadow-lg hover:bg-gray-700 dark:hover:bg-gray-600 transition-all duration-300 z-50"
      aria-label="Наверх"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" />
      </svg>
    </button>
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
const selectedFiles = ref([])
const imageNames = ref([])
const searchInput = ref(null)
const previewUrls = ref([])
const uploadProgress = ref([])
const showAnchor = ref(false)
const isUploading = ref(false)

// Add new refs for pagination
const currentPage = ref(1)
const imagesPerPage = ref(12)
const allImages = ref([])
const loadingMore = ref(false)
const hasMoreImages = ref(true)
const observerTarget = ref(null)

const API_BASE_URL = '/api'

// Mock data for testing
const mockAlbums = [
  {
    tag: 'Все фото',
    thumbnail: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
  },
  {
    tag: 'Природа',
    thumbnail: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
  },
  {
    tag: 'Город',
    thumbnail: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
  },
  {
    tag: 'Технологии',
    thumbnail: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
  },
  {
    tag: 'Еда',
    thumbnail: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
  },
  {
    tag: 'Путешествия',
    thumbnail: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
  },
  {
    tag: 'Архитектура',
    thumbnail: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
  },
  {
    tag: 'Животные',
    thumbnail: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
  },
  {
    tag: 'Искусство',
    thumbnail: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
  }
]

const mockImages = {
  all: [
    // Default photos
    {
      id: 1,
      filename: 'Недавнее фото 1',
      tags: [{ name: 'Природа' }, { name: 'Недавнее' }],
      url: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
    },
    {
      id: 2,
      filename: 'Недавнее фото 2',
      tags: [{ name: 'Город' }, { name: 'Недавнее' }],
      url: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
    },
    {
      id: 3,
      filename: 'Недавнее фото 3',
      tags: [{ name: 'Технологии' }, { name: 'Недавнее' }],
      url: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
    },
    {
      id: 4,
      filename: 'Недавнее фото 4',
      tags: [{ name: 'Еда' }, { name: 'Недавнее' }],
      url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
    },
    // Nature photos
    {
      id: 5,
      filename: 'Природа фото 1',
      tags: [{ name: 'Природа' }, { name: 'Пейзаж' }],
      url: 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=400&h=300&fit=crop'
    },
    {
      id: 6,
      filename: 'Природа фото 2',
      tags: [{ name: 'Природа' }, { name: 'Горы' }],
      url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=400&h=300&fit=crop'
    },
    {
      id: 7,
      filename: 'Природа фото 3',
      tags: [{ name: 'Природа' }, { name: 'Лес' }],
      url: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&h=300&fit=crop'
    },
    {
      id: 8,
      filename: 'Природа фото 4',
      tags: [{ name: 'Природа' }, { name: 'Океан' }],
      url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'
    },
    // City photos
    {
      id: 9,
      filename: 'Город фото 1',
      tags: [{ name: 'Город' }, { name: 'Городской' }],
      url: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=400&h=300&fit=crop'
    },
    {
      id: 10,
      filename: 'Город фото 2',
      tags: [{ name: 'Город' }, { name: 'Архитектура' }],
      url: 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=400&h=300&fit=crop'
    },
    {
      id: 11,
      filename: 'Город фото 3',
      tags: [{ name: 'Город' }, { name: 'Улица' }],
      url: 'https://images.unsplash.com/photo-1449157291145-7efd050a4d0e?w=400&h=300&fit=crop'
    },
    {
      id: 12,
      filename: 'Город фото 4',
      tags: [{ name: 'Город' }, { name: 'Ночь' }],
      url: 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=400&h=300&fit=crop'
    },
    // Technology photos
    {
      id: 13,
      filename: 'Технологии фото 1',
      tags: [{ name: 'Технологии' }, { name: 'Устройства' }],
      url: 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop'
    },
    {
      id: 14,
      filename: 'Технологии фото 2',
      tags: [{ name: 'Технологии' }, { name: 'Инновации' }],
      url: 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=300&fit=crop'
    },
    {
      id: 15,
      filename: 'Технологии фото 3',
      tags: [{ name: 'Технологии' }, { name: 'ИИ' }],
      url: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop'
    },
    {
      id: 16,
      filename: 'Технологии фото 4',
      tags: [{ name: 'Технологии' }, { name: 'Робототехника' }],
      url: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=400&h=300&fit=crop'
    },
    // Food photos
    {
      id: 17,
      filename: 'Еда фото 1',
      tags: [{ name: 'Еда' }, { name: 'Кухня' }],
      url: 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=400&h=300&fit=crop'
    },
    {
      id: 18,
      filename: 'Еда фото 2',
      tags: [{ name: 'Еда' }, { name: 'Ресторан' }],
      url: 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop'
    },
    {
      id: 19,
      filename: 'Еда фото 3',
      tags: [{ name: 'Еда' }, { name: 'Десерт' }],
      url: 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=400&h=300&fit=crop'
    },
    {
      id: 20,
      filename: 'Еда фото 4',
      tags: [{ name: 'Еда' }, { name: 'Здоровое' }],
      url: 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=400&h=300&fit=crop'
    },
    // Travel photos
    {
      id: 21,
      filename: 'Путешествия фото 1',
      tags: [{ name: 'Путешествия' }, { name: 'Приключения' }],
      url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
    },
    {
      id: 22,
      filename: 'Путешествия фото 2',
      tags: [{ name: 'Путешествия' }, { name: 'Пейзаж' }],
      url: 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=400&h=300&fit=crop'
    },
    {
      id: 23,
      filename: 'Путешествия фото 3',
      tags: [{ name: 'Путешествия' }, { name: 'Культура' }],
      url: 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=400&h=300&fit=crop'
    },
    {
      id: 24,
      filename: 'Путешествия фото 4',
      tags: [{ name: 'Путешествия' }, { name: 'Пляж' }],
      url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&h=300&fit=crop'
    },
    // Architecture photos
    {
      id: 25,
      filename: 'Архитектура фото 1',
      tags: [{ name: 'Архитектура' }, { name: 'Современная' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 26,
      filename: 'Архитектура фото 2',
      tags: [{ name: 'Архитектура' }, { name: 'Классическая' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 27,
      filename: 'Архитектура фото 3',
      tags: [{ name: 'Архитектура' }, { name: 'Интерьер' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    {
      id: 28,
      filename: 'Архитектура фото 4',
      tags: [{ name: 'Архитектура' }, { name: 'Дизайн' }],
      url: 'https://images.unsplash.com/photo-1487958449943-2429e8be8625?w=400&h=300&fit=crop'
    },
    // Animals photos
    {
      id: 29,
      filename: 'Животные фото 1',
      tags: [{ name: 'Животные' }, { name: 'Дикая природа' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 30,
      filename: 'Животные фото 2',
      tags: [{ name: 'Животные' }, { name: 'Питомцы' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 31,
      filename: 'Животные фото 3',
      tags: [{ name: 'Животные' }, { name: 'Природа' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    {
      id: 32,
      filename: 'Животные фото 4',
      tags: [{ name: 'Животные' }, { name: 'Птицы' }],
      url: 'https://images.unsplash.com/photo-1474314170901-f351b68f544f?w=400&h=300&fit=crop'
    },
    // Art photos
    {
      id: 33,
      filename: 'Искусство фото 1',
      tags: [{ name: 'Искусство' }, { name: 'Живопись' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 34,
      filename: 'Искусство фото 2',
      tags: [{ name: 'Искусство' }, { name: 'Скульптура' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 35,
      filename: 'Искусство фото 3',
      tags: [{ name: 'Искусство' }, { name: 'Цифровое' }],
      url: 'https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?w=400&h=300&fit=crop'
    },
    {
      id: 36,
      filename: 'Искусство фото 4',
      tags: [{ name: 'Искусство' }, { name: 'Фотография' }],
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
    console.error('Ошибка получения предложений:', error)
  }
}, 300)

// Modify performSearch to handle pagination
const performSearch = async () => {
  suggestions.value = []
  try {
    if (selectedTag.value === 'Все фото' || !selectedTag.value) {
      allImages.value = mockImages.all
    } else {
      allImages.value = mockImages[selectedTag.value] || []
    }
    currentPage.value = 1
    loadInitialImages()
  } catch (error) {
    console.error('Ошибка поиска изображений:', error)
  }
}

// Add new function to load initial images
const loadInitialImages = () => {
  const start = 0
  const end = imagesPerPage.value
  images.value = allImages.value.slice(start, end)
  hasMoreImages.value = end < allImages.value.length
}

// Add new function to load more images
const loadMoreImages = () => {
  if (loadingMore.value || !hasMoreImages.value) return

  loadingMore.value = true
  
  setTimeout(() => {
    const start = currentPage.value * imagesPerPage.value
    const end = start + imagesPerPage.value
    const newImages = allImages.value.slice(start, end)
    
    images.value = [...images.value, ...newImages]
    currentPage.value++
    hasMoreImages.value = end < allImages.value.length
    loadingMore.value = false
  }, 300) // Small delay to prevent rapid loading
}

// Add intersection observer setup
const setupIntersectionObserver = () => {
  const options = {
    root: null,
    rootMargin: '100px',
    threshold: 0.1
  }

  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && !loadingMore.value && hasMoreImages.value) {
      loadMoreImages()
    }
  }, options)

  if (observerTarget.value) {
    observer.observe(observerTarget.value)
  }

  return observer
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
    albums.value = mockAlbums
  } catch (error) {
    console.error('Ошибка получения альбомов:', error)
  }
}

// Handle file selection
const handleFileSelect = (event) => {
  const files = event.target.files
  if (files.length > 0) {
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (file.type.startsWith('image/')) {
        selectedFiles.value.push(file)
        previewUrls.value.push(URL.createObjectURL(file))
      }
    }
  }
}

// Handle drag and drop
const handleDrop = (event) => {
  const files = event.dataTransfer.files
  if (files.length > 0) {
    for (let i = 0; i < files.length; i++) {
      const file = files[i]
      if (file.type.startsWith('image/')) {
        selectedFiles.value.push(file)
        previewUrls.value.push(URL.createObjectURL(file))
      }
    }
  }
}

// Close upload modal
const closeUploadModal = () => {
  showUploadModal.value = false
  selectedFiles.value = []
  previewUrls.value = []
  isUploading.value = false
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Update uploadImage function
const uploadImages = async () => {
  if (selectedFiles.value.length === 0) {
    alert('Пожалуйста, выберите изображения')
    return
  }

  isUploading.value = true
  uploadProgress.value = selectedFiles.value.map(() => 0)

  try {
    const uploadPromises = selectedFiles.value.map((file, index) => {
      const formData = new FormData()
      formData.append('file', file)

      return axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          uploadProgress.value[index] = percentCompleted
        }
      })
    })

    const responses = await Promise.all(uploadPromises)
    
    const imageResponses = await Promise.all(responses.map(async (response, index) => {
      const imageResponse = await axios.get(`${API_BASE_URL}/images/${response.data.id}`)
      return {
        id: response.data.id,
        filename: selectedFiles.value[index].name,
        tags: imageResponse.data.tags,
        url: URL.createObjectURL(selectedFiles.value[index])
      }
    }))
    
    images.value = [...imageResponses, ...images.value]
    closeUploadModal()
  } catch (error) {
    console.error('Ошибка загрузки изображений:', error)
    alert('Ошибка загрузки изображений. Пожалуйста, попробуйте снова.')
  } finally {
    isUploading.value = false
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
    link.setAttribute('download', 'изображение.jpg')
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    console.error('Ошибка скачивания изображения:', error)
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

// Add new function after the handleSearch function
const focusSearch = () => {
  searchInput.value?.focus()
}

// Add removeSelectedFile function
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
  previewUrls.value.splice(index, 1)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

// Add scroll to top function
const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

// Add scroll event handler
const handleScroll = () => {
  showAnchor.value = window.scrollY > 500
}

// Update showUploadModal watcher
watch(showUploadModal, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

// Initial load
onMounted(() => {
  initTheme()
  watchSystemTheme()
  fetchAlbums()
  performSearch()
  window.addEventListener('resize', handleResize)
  window.addEventListener('scroll', handleScroll)
  
  // Add scroll event listener to update button visibility
  if (albumContainer.value) {
    albumContainer.value.addEventListener('scroll', updateScrollButtons)
  }

  // Setup intersection observer
  const observer = setupIntersectionObserver()

  // Cleanup observer on unmount
  onUnmounted(() => {
    if (observerTarget.value) {
      observer.unobserve(observerTarget.value)
    }
  })
})

// Clean up event listener
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('scroll', handleScroll)
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

/* Apply Inter Medium font to modal elements and image names */
.modal-content, .font-medium {
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

/* Light theme styles */
body {
  background-color: #f2f1f1;
  color: #212020;
}

header{
  background-color: #212020;
}

/* Dark theme styles */
.dark {
  color-scheme: dark;
}

.dark body {
  background-color: #212020;
  color: #f2f1f1;
}

/* Update modal styles */
.bg-white {
  background-color: #f2f1f1;
}

/* POPUP BG COLOR */
.dark .bg-white.dark\:bg-black {
  background-color: #212020;
}

/* Update modal background in dark theme */
.dark .bg-white {
  background-color: #212020;
} 

/* Update image card background */
.bg-white.rounded-lg {
  background-color: #ffffff !important;
}

.dark .bg-white.rounded-lg {
  background-color: #282828 !important;
}

.tag-bg {  
  background-color: #ABCDEFa6;
  color: #3E5F8A;
}

.tag-bg:hover {
  background-color: #7caedfa6;
}

.dark .tag-bg {
  background-color: #7134d26e;
  color: #e2d5f6;
}

.dark .tag-bg:hover {
  background-color: #6232afa6;
}

/* Update text colors */
.text-gray-900 {
  color: #212020 !important;
}

.dark .text-gray-900 {
  color: #f2f1f1 !important;
}

/* Update modal text colors */
.text-gray-600 {
  color: #212020 !important;
}

.bg-search{
  background-color: #212020;
}

.dark .text-gray-600 {
  color: #f2f1f1 !important;
}

/* Update input styles */
input {
  background-color: #f2f1f1;
  color: #212020;
}

.dark input {
  background-color: #212020;
  color: #f2f1f1;
}

/* Update suggestions dropdown */
.bg-white.rounded-md {
  background-color: #f2f1f1;
  border: 1px solid #e5e7eb;
}

.dark .bg-white.rounded-md {
  background-color: #212020;
  border: 1px solid #4a4a4a;
}

/* Update hover states */
.hover\:bg-gray-100:hover {
  background-color: #e5e7eb;
  color: #1f1d1d;
}

.dark .hover\:bg-gray-100:hover {
  background-color: #2d2d2d;
  color: #f3f3f3;
}

.footer-gradient {
  background: linear-gradient(to bottom, #1a1a1a, #000000);
}

.dark .footer-gradient {
  background: linear-gradient(to bottom, #1a1a1a, #000000);
}

/* Add rotating dots animation */
.loading-spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #ABCDEFa6;
  border-bottom-color: transparent;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.dark .loading-spinner {
  border-color: #7134d26e;
  border-bottom-color: transparent;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style> 