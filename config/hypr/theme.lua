-- Shared Hyprland layout. Palette border colors come from the active theme pack.
return hl.config({
  general = {
    gaps_in = 5, gaps_out = 10, border_size = 2,
  },
  decoration = { rounding = 6, blur = { enabled = false } },
  animations = { enabled = false },
})
