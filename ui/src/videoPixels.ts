export function framePixelFromClick(
  clientX: number,
  clientY: number,
  video: HTMLVideoElement,
): { x_px: number; y_px: number } | null {
  if (video.videoWidth === 0 || video.videoHeight === 0) {
    return null
  }
  const rect = video.getBoundingClientRect()
  const scale = Math.min(rect.width / video.videoWidth, rect.height / video.videoHeight)
  const contentWidth = video.videoWidth * scale
  const contentHeight = video.videoHeight * scale
  const originX = rect.left + (rect.width - contentWidth) / 2
  const originY = rect.top + (rect.height - contentHeight) / 2
  const x_px = (clientX - originX) / scale
  const y_px = (clientY - originY) / scale
  if (x_px < 0 || y_px < 0 || x_px > video.videoWidth || y_px > video.videoHeight) {
    return null
  }
  return { x_px, y_px }
}
