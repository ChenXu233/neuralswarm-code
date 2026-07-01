export type NextFn = (ctx?: any) => Promise<any>

export interface Middleware {
  (ctx: any, next: NextFn): Promise<any>
}

/**
 * 按顺序执行的 middleware 链。
 * 每个 middleware 接收当前 ctx 和一个 next() 函数。
 * 调用 next() 将控制权传递给下一个 middleware。
 * 不调用 next() 则终止链。
 */
export async function runPipeline(
  middlewares: Middleware[],
  initialCtx: any,
): Promise<any> {
  let idx = -1

  async function dispatch(i: number, ctx: any): Promise<any> {
    if (i <= idx) {
      throw new Error('next() called multiple times')
    }
    idx = i
    const fn = middlewares[i]
    if (!fn) return ctx
    return fn(ctx, (nextCtx?: any) => dispatch(i + 1, nextCtx ?? ctx))
  }

  return dispatch(0, initialCtx)
}
