import { ref, watch, onUnmounted, computed, type Ref } from 'vue'

export interface UseBottomSheetDragOptions {
  show: Ref<boolean>
  bottomSheetOnMobile?: Ref<boolean>
  swipeToClose?: Ref<boolean>
  dismissible?: Ref<boolean>
  onClose: () => void
}

export function useBottomSheetDrag(options: UseBottomSheetDragOptions) {
  const panelRef = ref<HTMLElement | null>(null)
  const bodyRef = ref<HTMLElement | null>(null)

  const isDragging = ref(false)
  const isDismissing = ref(false)
  const dragOffset = ref(0)

  let startY = 0
  let lastY = 0
  let lastTime = 0
  let velocity = 0
  let bodyScrollTopAtStart = 0

  // Scroll lock & state reset
  watch(
    options.show,
    (isOpen) => {
      dragOffset.value = 0
      isDragging.value = false
      isDismissing.value = false
      if (typeof document === 'undefined') return
      document.body.style.overflow = isOpen ? 'hidden' : ''
    },
    { immediate: true },
  )

  onUnmounted(() => {
    if (typeof document !== 'undefined') {
      document.body.style.overflow = ''
    }
  })

  function startDrag(clientY: number) {
    if (options.swipeToClose?.value === false || options.dismissible?.value === false) return
    isDragging.value = true
    startY = clientY
    lastY = clientY
    lastTime = performance.now()
    velocity = 0
  }

  function updateDrag(clientY: number) {
    if (!isDragging.value) return
    const now = performance.now()
    const dt = now - lastTime
    if (dt > 0) {
      velocity = (clientY - lastY) / dt
    }
    lastY = clientY
    lastTime = now

    const deltaY = clientY - startY
    if (deltaY > 0) {
      dragOffset.value = deltaY
    } else {
      // Elastic rubber-band resistance when pulling up past top edge
      dragOffset.value = Math.max(-20, deltaY * 0.15)
    }
  }

  function finishDrag() {
    if (!isDragging.value) return
    isDragging.value = false

    const panelHeight = panelRef.value?.offsetHeight || 400
    const threshold = Math.min(110, panelHeight * 0.22)
    const shouldDismiss =
      dragOffset.value > threshold || (dragOffset.value > 35 && velocity > 0.4)

    if (
      shouldDismiss &&
      options.dismissible?.value !== false &&
      options.swipeToClose?.value !== false
    ) {
      isDismissing.value = true
      dragOffset.value = panelHeight
      setTimeout(() => {
        options.onClose()
        dragOffset.value = 0
        isDismissing.value = false
      }, 220)
    } else {
      // Spring back smoothly
      dragOffset.value = 0
    }
  }

  // Pointer event handlers for Grab Handle & Header
  function onHandlePointerDown(e: PointerEvent) {
    if (e.button !== 0) return
    ;(e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId)
    startDrag(e.clientY)
  }

  function onHandlePointerMove(e: PointerEvent) {
    updateDrag(e.clientY)
  }

  function onHandlePointerUp(e: PointerEvent) {
    try {
      ;(e.currentTarget as HTMLElement).releasePointerCapture?.(e.pointerId)
    } catch {}
    finishDrag()
  }

  function onHeaderPointerDown(e: PointerEvent) {
    const target = e.target as HTMLElement
    if (target.closest('button, a, input, select, textarea, [data-no-drag]')) {
      return
    }
    onHandlePointerDown(e)
  }

  // Touch event handlers on scrollable panel/body
  function onTouchStart(e: TouchEvent) {
    if (options.swipeToClose?.value === false || options.dismissible?.value === false) return
    if (window.innerWidth >= 640 && options.bottomSheetOnMobile?.value === false) return
    if (e.touches.length !== 1) return

    const target = e.target as HTMLElement
    if (target.closest('input, textarea, select, button, a, [contenteditable="true"]')) {
      return
    }

    const touch = e.touches[0]
    startY = touch.clientY
    lastY = touch.clientY
    lastTime = performance.now()
    velocity = 0

    const bodyEl = bodyRef.value
    bodyScrollTopAtStart = bodyEl ? bodyEl.scrollTop : 0
  }

  function onTouchMove(e: TouchEvent) {
    if (e.touches.length !== 1) return
    const touch = e.touches[0]
    const now = performance.now()
    const dt = now - lastTime
    if (dt > 0) {
      velocity = (touch.clientY - lastY) / dt
    }
    lastY = touch.clientY
    lastTime = now

    const deltaY = touch.clientY - startY
    const bodyEl = bodyRef.value
    const currentScrollTop = bodyEl ? bodyEl.scrollTop : 0

    if (isDragging.value) {
      if (e.cancelable) e.preventDefault()
      if (deltaY > 0) {
        dragOffset.value = deltaY
      } else {
        dragOffset.value = Math.max(-20, deltaY * 0.15)
      }
      return
    }

    // Initiate drag from content if at top (scrollTop <= 0) and dragging downward
    if (currentScrollTop <= 0 && bodyScrollTopAtStart <= 0 && deltaY > 10) {
      isDragging.value = true
      if (e.cancelable) e.preventDefault()
      dragOffset.value = deltaY - 10
    }
  }

  function onTouchEnd() {
    if (isDragging.value) {
      finishDrag()
    }
  }

  // Dynamic CSS transforms
  const panelStyle = computed(() => {
    if (isDismissing.value) {
      return {
        transform: 'translateY(100%)',
        transition: 'transform 0.22s cubic-bezier(0.32, 0.72, 0, 1)',
      }
    }
    if (isDragging.value) {
      return {
        transform: `translateY(${dragOffset.value}px)`,
        transition: 'none',
        willChange: 'transform',
      }
    }
    if (dragOffset.value !== 0) {
      return {
        transform: 'translateY(0px)',
        transition: 'transform 0.28s cubic-bezier(0.32, 0.72, 0, 1)',
      }
    }
    return {}
  })

  const backdropStyle = computed(() => {
    if (isDismissing.value) {
      return {
        opacity: 0,
        transition: 'opacity 0.22s ease-out',
      }
    }
    if (isDragging.value && dragOffset.value > 0) {
      const panelHeight = panelRef.value?.offsetHeight || 400
      const progress = Math.min(dragOffset.value / panelHeight, 1)
      return {
        opacity: Math.max(0.15, 1 - progress * 0.85),
        transition: 'none',
      }
    }
    return {}
  })

  return {
    panelRef,
    bodyRef,
    isDragging,
    isDismissing,
    dragOffset,
    panelStyle,
    backdropStyle,
    onHandlePointerDown,
    onHandlePointerMove,
    onHandlePointerUp,
    onHeaderPointerDown,
    onTouchStart,
    onTouchMove,
    onTouchEnd,
  }
}
