-- Hexen's initial palette. Keep colors and spacing here; no theme framework.
return hl.config({
  general = {
    gaps_in = 5, gaps_out = 10, border_size = 2,
    col = { active_border = 'rgb(7aa2f7)', inactive_border = 'rgb(414868)' },
  },
  decoration = { rounding = 6, blur = { enabled = false } },
  animations = { enabled = false },
})
