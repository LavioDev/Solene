export interface ThemePreset {
  id: string
  nameKey: string
  primaryHex: string
  previewColor: string
  shades: {
    50: string
    100: string
    200: string
    300: string
    400: string
    500: string
    600: string
    700: string
    800: string
    900: string
    950: string
  }
}

export const THEME_PRESETS: ThemePreset[] = [
  {
    id: 'violet',
    nameKey: 'theme.presetViolet',
    primaryHex: '#7c3aed',
    previewColor: '#7c3aed',
    shades: {
      50: '245 243 255',
      100: '237 233 254',
      200: '221 214 254',
      300: '196 181 253',
      400: '167 139 250',
      500: '139 92 246',
      600: '124 58 237',
      700: '109 40 217',
      800: '91 33 182',
      900: '59 7 100',
      950: '46 16 101',
    },
  },
  {
    id: 'blue',
    nameKey: 'theme.presetBlue',
    primaryHex: '#2563eb',
    previewColor: '#2563eb',
    shades: {
      50: '239 246 255',
      100: '219 234 254',
      200: '191 219 254',
      300: '147 197 253',
      400: '96 165 250',
      500: '59 130 246',
      600: '37 99 235',
      700: '29 78 216',
      800: '30 64 175',
      900: '30 58 138',
      950: '23 37 84',
    },
  },
  {
    id: 'emerald',
    nameKey: 'theme.presetEmerald',
    primaryHex: '#059669',
    previewColor: '#059669',
    shades: {
      50: '236 253 245',
      100: '209 250 229',
      200: '167 243 208',
      300: '110 231 183',
      400: '52 211 153',
      500: '16 185 129',
      600: '5 150 105',
      700: '4 120 87',
      800: '6 95 70',
      900: '6 78 59',
      950: '2 44 34',
    },
  },
  {
    id: 'rose',
    nameKey: 'theme.presetRose',
    primaryHex: '#e11d48',
    previewColor: '#e11d48',
    shades: {
      50: '255 241 242',
      100: '255 228 230',
      200: '254 205 211',
      300: '253 164 175',
      400: '251 113 133',
      500: '244 63 94',
      600: '225 29 72',
      700: '190 18 60',
      800: '159 18 57',
      900: '136 19 55',
      950: '76 5 25',
    },
  },
  {
    id: 'yellow',
    nameKey: 'theme.presetYellow',
    primaryHex: '#f5ae19',
    previewColor: '#feca3b',
    shades: {
      50: '255 252 235',
      100: '254 246 201',
      200: '254 236 156',
      300: '253 221 106',
      400: '251 202 59',
      500: '245 174 25',
      600: '226 144 14',
      700: '189 110 13',
      800: '150 84 17',
      900: '122 69 19',
      950: '68 35 9',
    },
  },
  {
    id: 'amber',
    nameKey: 'theme.presetAmber',
    primaryHex: '#d97706',
    previewColor: '#d97706',
    shades: {
      50: '255 251 235',
      100: '254 243 199',
      200: '253 230 138',
      300: '252 211 77',
      400: '251 191 36',
      500: '245 158 11',
      600: '217 119 6',
      700: '180 83 9',
      800: '146 64 14',
      900: '120 53 15',
      950: '69 26 3',
    },
  },
  {
    id: 'cyan',
    nameKey: 'theme.presetCyan',
    primaryHex: '#0891b2',
    previewColor: '#0891b2',
    shades: {
      50: '236 254 255',
      100: '207 250 254',
      200: '165 243 252',
      300: '103 232 249',
      400: '34 211 238',
      500: '6 182 212',
      600: '8 145 178',
      700: '14 116 144',
      800: '21 94 117',
      900: '22 78 99',
      950: '8 51 68',
    },
  },
  {
    id: 'indigo',
    nameKey: 'theme.presetIndigo',
    primaryHex: '#4f46e5',
    previewColor: '#4f46e5',
    shades: {
      50: '238 242 255',
      100: '224 231 255',
      200: '199 210 254',
      300: '165 180 252',
      400: '129 140 248',
      500: '99 102 241',
      600: '79 70 229',
      700: '67 56 202',
      800: '55 48 163',
      900: '49 46 129',
      950: '30 27 75',
    },
  },
  {
    id: 'pink',
    nameKey: 'theme.presetPink',
    primaryHex: '#db2777',
    previewColor: '#db2777',
    shades: {
      50: '253 242 248',
      100: '252 231 243',
      200: '251 207 232',
      300: '249 168 212',
      400: '244 114 182',
      500: '236 72 153',
      600: '219 39 119',
      700: '190 24 93',
      800: '157 23 77',
      900: '131 24 67',
      950: '80 7 36',
    },
  },
]

export const DEFAULT_THEME_ID = 'violet'

export function applyThemeToCssVars(theme: ThemePreset) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  Object.entries(theme.shades).forEach(([step, rgbVal]) => {
    root.style.setProperty(`--color-primary-${step}`, rgbVal)
  })
}
