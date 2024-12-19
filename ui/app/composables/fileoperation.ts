import slugify from 'slugify'

export const useFileSlugifyOperation = (file: File) => {
  return slugify(file.name, { replacement: '_', lower: true })
}


