import type { LibraryStatus } from './api'

type CoverageStatus = Pick<LibraryStatus,
  'source_status' | 'source_files' | 'indexed_files'>

/** 源目录不可读时覆盖率未知,不能把 null 当 0 算出虚假的 100%。 */
export function coveragePercentage(status: CoverageStatus | null): number | null {
  if (!status || status.source_status !== 'ok' || status.source_files === null) return null
  const raw = status.indexed_files / Math.max(status.source_files, 1) * 100
  // 未满覆盖不能四舍五入成 100%,否则与待入库数量矛盾。
  return raw >= 100 ? 100 : Math.min(99.9, Math.floor(raw * 10) / 10)
}

/**
 * 是否出现了新的真实入库完成标记。
 * 用 finished_at 而不是 phase 转换:很小的增量可能在两次轮询之间完成,
 * 页面从未观察到运行阶段;空 await 的“无需更新”不写 finished_at,也不算新入库。
 */
export function ingestFinishedSince(lastFinishedAt: string | undefined,
                                    nextFinishedAt: string | undefined): boolean {
  return Boolean(nextFinishedAt) && nextFinishedAt !== lastFinishedAt
}
