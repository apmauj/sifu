import { render } from '@testing-library/react'
import { act } from 'react'

// Renders a component and awaits microtask & macro task queues to settle common async setState
export async function renderAsync(ui, options) {
  let utils
  await act(async () => {
    utils = render(ui, options)
    // allow any immediate promises (effects) to flush
    await Promise.resolve()
  })
  return utils
}

export async function actFlush() {
  await act(async () => {
    await Promise.resolve()
  })
}
