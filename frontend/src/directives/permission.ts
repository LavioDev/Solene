import type { Directive, DirectiveBinding } from 'vue'
import { useAuthStore } from '@/stores/authStore'

export const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding<string | string[]>) {
    const authStore = useAuthStore()
    const value = binding.value

    if (!value) return

    let hasAccess = false
    if (Array.isArray(value)) {
      hasAccess = value.some((perm) => authStore.hasPermission(perm))
    } else {
      hasAccess = authStore.hasPermission(value)
    }

    if (!hasAccess) {
      el.parentNode?.removeChild(el)
    }
  },
}
