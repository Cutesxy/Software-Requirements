<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">用户登录</h1>
        <p class="login-subtitle">User Authentication</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder=""
            required
            autocomplete="username"
            :disabled="loading"
          />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder=""
            required
            autocomplete="current-password"
            :disabled="loading"
          />
        </div>

        <div v-if="errorMessage" class="error-message">
          {{ errorMessage }}
        </div>

        <button
          type="submit"
          class="login-button"
          :disabled="loading"
        >
          <span v-if="loading">Signing in...</span>
          <span v-else>Sign In</span>
        </button>
      </form>

    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      loading: false,
      errorMessage: ''
    }
  },
  methods: {
    ...mapActions(['login']),
    
    async handleLogin() {
      this.errorMessage = ''
      this.loading = true

      try {
        const result = await this.login({
          username: this.form.username,
          password: this.form.password
        })

        if (result.success) {
          // 登录成功，跳转到首页
          const redirect = this.$route.query.redirect || '/overview'
          this.$router.push(redirect)
        } else {
          this.errorMessage = result.message || '登录失败'
        }
      } catch (error) {
        console.error('Login error:', error)
        this.errorMessage = '登录失败，请检查网络连接'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ffffff;
  padding: 40px 20px;
}

.login-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  width: 100%;
  max-width: 400px;
  padding: 60px 50px;
}

.login-header {
  text-align: left;
  margin-bottom: 48px;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 24px;
}

.login-title {
  font-size: 24px;
  font-weight: 400;
  color: #111827;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
}

.login-subtitle {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  font-weight: 400;
}

.login-form {
  .form-group {
    margin-bottom: 28px;

    label {
      display: block;
      font-size: 12px;
      font-weight: 500;
      color: #374151;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    input {
      width: 100%;
      padding: 10px 0;
      font-size: 14px;
      border: none;
      border-bottom: 1px solid #d1d5db;
      background: transparent;
      color: #111827;
      transition: border-color 0.2s ease;
      box-sizing: border-box;
      font-family: inherit;

      &:focus {
        outline: none;
        border-bottom-color: #111827;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        border-bottom-color: #e5e7eb;
      }

      &::placeholder {
        color: #9ca3af;
        font-weight: 300;
      }
    }
  }

  .error-message {
    padding: 12px 0;
    color: #dc2626;
    font-size: 13px;
    margin-bottom: 20px;
    border-bottom: 1px solid #fee2e2;
  }

  .login-button {
    width: 100%;
    padding: 12px 0;
    font-size: 14px;
    font-weight: 500;
    color: #111827;
    background: transparent;
    border: 1px solid #111827;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: inherit;

    &:hover:not(:disabled) {
      background: #111827;
      color: #ffffff;
    }

    &:active:not(:disabled) {
      background: #374151;
      border-color: #374151;
    }

    &:disabled {
      opacity: 0.4;
      cursor: not-allowed;
      border-color: #d1d5db;
    }
  }
}

.login-footer {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
  text-align: left;

  .hint-text {
    font-size: 11px;
    color: #9ca3af;
    margin: 0;
    font-weight: 300;
    letter-spacing: 0.02em;
  }
}
</style>

