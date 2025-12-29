<template>
  <div class="data-table-wrapper">
    <div v-if="$slots.header" class="table-header">
      <slot name="header"></slot>
    </div>
    
    <div class="table-container" :style="{ maxHeight: maxHeight + 'px' }">
      <table class="table">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              :style="{ width: col.width }"
              @click="col.sortable && onSort(col.key)"
              :class="{ sortable: col.sortable }"
            >
              <span>{{ col.label }}</span>
              <span v-if="col.sortable && sortKey === col.key" class="sort-icon">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, index) in sortedData"
            :key="index"
            @click="onRowClick(row)"
            :class="{ clickable: clickable }"
          >
            <td v-for="col in columns" :key="col.key">
              <slot :name="`col-${col.key}`" :row="row" :value="row[col.key]">
                <span
                  v-if="col.type === 'number'"
                  class="value-display"
                  :class="getNumberClass(row[col.key])"
                >
                  {{ formatNumber(row[col.key], col.decimals) }}
                </span>
                <span v-else-if="col.type === 'percent'" class="value-display">
                  {{ formatPercent(row[col.key]) }}
                </span>
                <span v-else-if="col.type === 'time'">
                  {{ formatTime(row[col.key]) }}
                </span>
                <span v-else>
                  {{ row[col.key] }}
                </span>
              </slot>
            </td>
          </tr>
          
          <tr v-if="!sortedData || sortedData.length === 0" class="empty-row">
            <td :colspan="columns.length">
              <div class="empty-state">
                <span>暂无数据</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="pageable && totalRows > pageSize" class="table-footer">
      <div class="pagination">
        <button
          class="btn-page"
          :disabled="currentPage === 1"
          @click="onPageChange(currentPage - 1)"
        >
          ‹
        </button>
        <span class="page-info">
          {{ currentPage }} / {{ totalPages }}
        </span>
        <button
          class="btn-page"
          :disabled="currentPage === totalPages"
          @click="onPageChange(currentPage + 1)"
        >
          ›
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  
  props: {
    columns: {
      type: Array,
      required: true
    },
    data: {
      type: Array,
      default: () => []
    },
    maxHeight: {
      type: Number,
      default: 600
    },
    clickable: {
      type: Boolean,
      default: false
    },
    pageable: {
      type: Boolean,
      default: false
    },
    pageSize: {
      type: Number,
      default: 50
    }
  },
  
  data() {
    return {
      sortKey: '',
      sortOrder: 'desc',
      currentPage: 1
    }
  },
  
  computed: {
    sortedData() {
      let result = [...(this.data || [])]
      
      if (this.sortKey) {
        result.sort((a, b) => {
          const aVal = a[this.sortKey]
          const bVal = b[this.sortKey]
          
          if (typeof aVal === 'number' && typeof bVal === 'number') {
            return this.sortOrder === 'asc' ? aVal - bVal : bVal - aVal
          }
          
          const aStr = String(aVal)
          const bStr = String(bVal)
          return this.sortOrder === 'asc'
            ? aStr.localeCompare(bStr)
            : bStr.localeCompare(aStr)
        })
      }
      
      if (this.pageable) {
        const start = (this.currentPage - 1) * this.pageSize
        const end = start + this.pageSize
        return result.slice(start, end)
      }
      
      return result
    },
    
    totalRows() {
      return this.data?.length || 0
    },
    
    totalPages() {
      return Math.ceil(this.totalRows / this.pageSize)
    }
  },
  
  methods: {
    onSort(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc'
      } else {
        this.sortKey = key
        this.sortOrder = 'desc'
      }
    },
    
    onRowClick(row) {
      if (this.clickable) {
        this.$emit('row-click', row)
      }
    },
    
    onPageChange(page) {
      this.currentPage = page
      this.$emit('page-change', page)
    },
    
    formatNumber(value, decimals = 2) {
      if (value === null || value === undefined) return '-'
      return Number(value).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
      })
    },
    
    formatPercent(value) {
      if (value === null || value === undefined) return '-'
      return (value * 100).toFixed(2) + '%'
    },
    
    formatTime(timestamp) {
      if (!timestamp) return '-'
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    },
    
    getNumberClass(value) {
      if (value > 0) return 'positive'
      if (value < 0) return 'negative'
      return 'neutral'
    }
  }
}
</script>

<style lang="scss" scoped>
.data-table-wrapper {
  background: $bg-card;
  border-radius: $border-radius;
  overflow: hidden;
}

.table-header {
  padding: 16px 20px;
  border-bottom: 1px solid $border-color;
}

.table-container {
  overflow-x: auto;
  overflow-y: auto;
  
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
}

.table {
  thead {
    position: sticky;
    top: 0;
    z-index: 10;
    
    th {
      &.sortable {
        cursor: pointer;
        user-select: none;
        
        &:hover {
          background: lighten($bg-secondary, 3%);
        }
      }
      
      span {
        display: inline-flex;
        align-items: center;
        gap: 4px;
      }
      
      .sort-icon {
        font-size: 12px;
        color: $color-primary;
      }
    }
  }
  
  tbody {
    tr {
      &.clickable {
        cursor: pointer;
      }
      
      &.empty-row {
        &:hover {
          background: transparent;
        }
      }
    }
  }
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: $text-tertiary;
  font-size: 14px;
}

.table-footer {
  display: flex;
  justify-content: center;
  padding: 16px;
  border-top: 1px solid $border-color;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-page {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: $bg-secondary;
  border: 1px solid $border-color;
  border-radius: 6px;
  color: $text-primary;
  font-size: 16px;
  cursor: pointer;
  transition: all $transition-fast;
  
  &:hover:not(:disabled) {
    border-color: $color-primary;
    color: $color-primary;
  }
  
  &:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
}

.page-info {
  font-size: 13px;
  color: $text-secondary;
  min-width: 60px;
  text-align: center;
}
</style>

