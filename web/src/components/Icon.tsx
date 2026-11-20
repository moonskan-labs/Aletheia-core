// Line icons from Skanda's layout C (#46), one stroke for all.
const paths = {
  search: 'M20.5 20.5 16 16 M18 10.5a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0',
  enter: 'M19 5v8a2 2 0 0 1-2 2H5m5-5-5 5 5 5',
  globe: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0 M3 12h18 M12 3c-5.5 5.5-5.5 12.5 0 18 5.5-5.5 5.5-12.5 0-18Z',
  fingerprint:
    'M3.5 12a8.5 8.5 0 0 1 17 0c0 2.5-.2 4.1-.6 5.7 M4.2 17c.9-1.3 1.6-3 1.6-5a6.2 6.2 0 0 1 12.4 0c0 3.9-.7 6.7-1.9 8.9 M6.1 20.1c1.7-2.3 2.6-5 2.6-8.1a3.3 3.3 0 1 1 6.6 0c0 4-.8 7.3-2.3 10 M9.4 21.9c1.7-3.2 2.6-6.3 2.6-10',
}

export type IconName = keyof typeof paths

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.55"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d={paths[name]} />
    </svg>
  )
}
