import { readFileSync, writeFileSync, existsSync } from 'fs'
import { resolve } from 'path'
import { createHash } from 'crypto'

const LLM_API_URL = process.env.LLM_API_URL || 'http://localhost:8000/v1/chat/completions'
const LLM_API_KEY = process.env.LLM_API_KEY || ''
const LLM_MODEL = process.env.LLM_MODEL || 'gpt-4'
const BATCH_SIZE = 50

interface TranslationMeta {
  [key: string]: string
}

function contentHash(text: string): string {
  return createHash('md5').update(text).digest('hex').slice(0, 8)
}

const LANG_NAMES: Record<string, string> = {
  zh: 'Chinese (Simplified)',
  jp: 'Japanese',
  ru: 'Russian'
}

async function translateBatch(
  entries: [string, string][],
  targetLang: string
): Promise<Record<string, string>> {
  const langName = LANG_NAMES[targetLang] || targetLang
  const prompt = entries
    .map(([key, value]) => `[${key}] ${value}`)
    .join('\n')

  const response = await fetch(LLM_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${LLM_API_KEY}`
    },
    body: JSON.stringify({
      model: LLM_MODEL,
      messages: [
        {
          role: 'system',
          content: `You are a professional translator. Translate each line to ${langName}.
Format: [key] translated_text
Keep the [key] unchanged. Only translate the text after the key.
Keep placeholders like {n}, {path}, {agentId} unchanged.
Return all translations, one per line.`
        },
        { role: 'user', content: prompt }
      ]
    })
  })

  const data = await response.json()
  const result = data.choices[0].message.content

  const translations: Record<string, string> = {}
  for (const line of result.split('\n')) {
    const match = line.match(/^\[(.+?)\]\s*(.+)$/)
    if (match) {
      translations[match[1]] = match[2]
    }
  }
  return translations
}

async function translateLocale(source: string, target: string) {
  const basePath = resolve(__dirname, '../src/locales')
  const sourcePath = resolve(basePath, `${source}.json`)
  const targetPath = resolve(basePath, `${target}.json`)
  const metaPath = resolve(basePath, `${target}.meta.json`)

  const sourceData: Record<string, string> = JSON.parse(readFileSync(sourcePath, 'utf-8'))
  const targetData: Record<string, string> = existsSync(targetPath)
    ? JSON.parse(readFileSync(targetPath, 'utf-8'))
    : {}
  const meta: TranslationMeta = existsSync(metaPath)
    ? JSON.parse(readFileSync(metaPath, 'utf-8'))
    : {}

  const toTranslate: [string, string][] = []
  for (const [key, value] of Object.entries(sourceData)) {
    const hash = contentHash(value)
    if (!meta[key] || meta[key] !== hash) {
      toTranslate.push([key, value])
    }
  }

  if (toTranslate.length === 0) {
    console.log(`[${target}] All translations up to date!`)
    return
  }

  console.log(`[${target}] Found ${toTranslate.length} keys to translate`)

  for (let i = 0; i < toTranslate.length; i += BATCH_SIZE) {
    const batch = toTranslate.slice(i, i + BATCH_SIZE)
    console.log(`[${target}] Translating batch ${Math.floor(i / BATCH_SIZE) + 1}/${Math.ceil(toTranslate.length / BATCH_SIZE)}...`)

    const translations = await translateBatch(batch, target)

    for (const [key, value] of Object.entries(translations)) {
      targetData[key] = value
      meta[key] = contentHash(sourceData[key])
    }
  }

  writeFileSync(targetPath, JSON.stringify(targetData, null, 2))
  writeFileSync(metaPath, JSON.stringify(meta, null, 2))
  console.log(`[${target}] Done! Translated ${toTranslate.length} keys`)
}

const args = process.argv.slice(2)
const sourceIdx = args.indexOf('--source')
const targetsIdx = args.indexOf('--targets')

if (sourceIdx === -1 || targetsIdx === -1) {
  console.error('Usage: npx tsx scripts/translate.ts --source en --targets zh,jp,ru')
  process.exit(1)
}

const source = args[sourceIdx + 1]
const targets = args[targetsIdx + 1].split(',')

;(async () => {
  for (const target of targets) {
    await translateLocale(source, target)
  }
})()
