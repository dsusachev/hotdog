export function proxyImage(url: string | null | undefined): string | undefined {
  if (!url) return undefined
  if (url.includes('www.themealdb.com/images/media/meals/')) {
    return url.replace('https://www.themealdb.com/images/media/meals/', '/img-proxy/meals/')
  }
  if (url.includes('images.openfoodfacts.org')) {
    try {
      return `/img-proxy/food${new URL(url).pathname}`
    } catch {
      return url
    }
  }
  return url
}
