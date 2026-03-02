// Vitest global test setup
import { config } from '@vue/test-utils'

// Suppress Naive UI console warnings in tests
config.global.config.warnHandler = () => null
