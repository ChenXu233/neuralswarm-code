import { describe, it, expect } from 'vitest'
import { runPipeline } from './pipeline'

describe('runPipeline', () => {
  it('executes middleware in order', async () => {
    const order: number[] = []
    const mw = [
      async (_ctx: any, next: any) => { order.push(1); return next() },
      async (_ctx: any, next: any) => { order.push(2); return next() },
      async (_ctx: any, next: any) => { order.push(3); return next() },
    ]
    const result = await runPipeline(mw, {})
    expect(order).toEqual([1, 2, 3])
  })

  it('passes modified context through next(ctx)', async () => {
    const mw = [
      async (ctx: any, next: any) => next({ ...ctx, step1: true }),
      async (ctx: any, next: any) => next({ ...ctx, step2: true }),
      async (ctx: any, _next: any) => ctx,
    ]
    const result = await runPipeline(mw, {})
    expect(result.step1).toBe(true)
    expect(result.step2).toBe(true)
  })

  it('terminates chain when middleware skips next()', async () => {
    const reached: boolean[] = []
    const mw = [
      async (_ctx: any, _next: any) => 'terminated',
      async (_ctx: any, next: any) => { reached.push(true); return next() },
    ]
    const result = await runPipeline(mw, {})
    expect(result).toBe('terminated')
    expect(reached).toEqual([])
  })

  it('throws when next() is called multiple times', async () => {
    const mw = [
      async (ctx: any, next: any) => {
        await next(ctx)
        await expect(next(ctx)).rejects.toThrow('next() called multiple times')
      },
    ]
    await runPipeline(mw, {})
  })

  it('returns initial context for empty middleware list', async () => {
    const result = await runPipeline([], { initial: true })
    expect(result.initial).toBe(true)
  })
})
