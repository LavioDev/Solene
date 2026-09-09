export type ModalWidth = 'sm' | 'md' | 'lg' | '880' | '1000' | '1200'

export interface AppModalProps {
  show: boolean
  title?: string
  width?: ModalWidth
  bottomSheetOnMobile?: boolean
  swipeToClose?: boolean
  dismissible?: boolean
  draggable?: boolean
  maximizable?: boolean
}

export const MODAL_WIDTH_CLASSES: Record<ModalWidth, string> = {
  sm: 'max-w-sm',
  md: 'sm:max-w-lg',
  lg: 'sm:max-w-2xl',
  '880': 'sm:max-w-[880px]',
  '1000': 'sm:max-w-[1000px]',
  '1200': 'sm:max-w-[1200px]',
}
