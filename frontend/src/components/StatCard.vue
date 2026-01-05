<template>
  <div class="stat-card" :class="{ hoverable: clickable }" @click="onClick">
    <div class="stat-header">
      <span class="stat-label">{{ label }}</span>
      <span v-if="icon" class="stat-icon" :style="{ color: iconColor }">{{ icon }}</span>
    </div>
    
    <div class="stat-value">
      <span
        class="value-text"
        :class="valueClass"
        :style="{ color: valueColor }"
      >
        {{ formattedValue }}
      </span>
      <span v-if="unit" class="value-unit">{{ unit }}</span>
    </div>
    
    <div v-if="change !== null && change !== undefined" class="stat-change">
      <span class="change-badge" :class="changeClass">
        <span class="change-arrow">{{ change >= 0 ? '↑' : '↓' }}</span>
        <span>{{ Math.abs(change).toFixed(2) }}%</span>
      </span>
      <span class="change-label">{{ changeLabel }}</span>
    </div>
    
    <div v-if="$slots.extra" class="stat-extra">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  
  props: {
    label: {
      type: String,
      required: true
    },
    value: {
      type: [Number, String],
      required: true
    },
    type: {
      type: String,
      default: 'number', // number, percent, currency
      validator: val => ['number', 'percent', 'currency', 'text'].includes(val)
    },
    decimals: {
      type: Number,
      default: 2
    },
    unit: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    },
    iconColor: {
      type: String,
      default: '#00C2FF'
    },
    valueColor: {
      type: String,
      default: ''
    },
    change: {
      type: Number,
      default: null
    },
    changeLabel: {
      type: String,
      default: '较昨日'
    },
    clickable: {
      type: Boolean,
      default: false
    }
  },
  
  computed: {
    formattedValue() {
      if (this.type === 'text') {
        return this.value
      }
      
      if (this.type === 'percent') {
        return (this.value * 100).toFixed(this.decimals)
      }
      
      if (this.type === 'currency') {
        return Number(this.value).toLocaleString('en-US', {
          minimumFractionDigits: this.decimals,
          maximumFractionDigits: this.decimals
        })
      }
      
      // number
      const num = Number(this.value)
      if (Math.abs(num) >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      }
      if (Math.abs(num) >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toLocaleString('en-US', {
        minimumFractionDigits: this.decimals,
        maximumFractionDigits: this.decimals
      })
    },
    
    valueClass() {
      if (this.valueColor) return ''
      
      const num = Number(this.value)
      if (num > 0) return 'positive'
      if (num < 0) return 'negative'
      return 'neutral'
    },
    
    changeClass() {
      if (this.change >= 0) return 'positive'
      return 'negative'
    }
  },
  
  methods: {
    onClick() {
      if (this.clickable) {
        this.$emit('click')
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.stat-card {
  background: $bg-card;
  border-radius: $border-radius;
  padding: 20px;
  box-shadow: $shadow-sm;
  transition: all $transition-normal;
  
  &.hoverable {
    cursor: pointer;
    
    &:hover {
      background: $bg-card-hover;
      box-shadow: $shadow-md;
      transform: translateY(-2px);
    }
  }
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-label {
  font-size: 13px;
  color: $text-secondary;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-icon {
  font-size: 20px;
  opacity: 0.8;
}

.stat-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
  margin-bottom: 8px;
}

.value-text {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
  
  &.positive {
    color: $color-success;
  }
  
  &.negative {
    color: $color-danger;
  }
  
  &.neutral {
    color: $text-primary;
  }
}

.value-unit {
  font-size: 16px;
  color: $text-tertiary;
  font-weight: 500;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.change-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  
  &.positive {
    background: rgba($color-success, 0.15);
    color: $color-success;
  }
  
  &.negative {
    background: rgba($color-danger, 0.15);
    color: $color-danger;
  }
  
  .change-arrow {
    font-size: 10px;
  }
}

.change-label {
  font-size: 11px;
  color: $text-tertiary;
}

.stat-extra {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid $border-color;
}
</style>

