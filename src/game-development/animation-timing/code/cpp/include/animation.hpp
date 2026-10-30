#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

namespace anim {
struct FrameRate {
  std::int64_t num{24}, den{1};
  FrameRate(std::int64_t n = 24, std::int64_t d = 1) : num(n), den(d) {
    if (n <= 0 || d <= 0) throw std::invalid_argument("positive rate required");
  }
  double time_at(std::int64_t frame) const {
    if (frame < 0) throw std::invalid_argument("negative frame");
    return static_cast<double>(frame) * den / num;
  }
};
inline double clamp01(double x) { return std::clamp(x, 0.0, 1.0); }
inline double smoothstep(double t) {
  t = clamp01(t);
  return t*t*(3-2*t);
}
struct Exposure { std::string drawing; int start{}, length{}; };
inline void validate_exposures(int total, const std::vector<Exposure>& exposures) {
  int cursor = 0;
  if (total < 0) throw std::invalid_argument("negative total");
  for (const auto& e: exposures) {
    if (e.drawing.empty() || e.length <= 0 || e.start != cursor)
      throw std::invalid_argument("invalid exposure interval");
    cursor += e.length;
  }
  if (cursor != total) throw std::invalid_argument("uncovered frames");
}
struct Body {
  double position{0}, velocity{0}, mass{1};
  void advance(double dt, double force) {
    if (!(mass > 0) || !(dt > 0) || !std::isfinite(dt) || !std::isfinite(force))
      throw std::invalid_argument("bad physics parameters");
    velocity += (force / mass) * dt;
    position += velocity * dt;
  }
};
struct Spring {
  double position{}, velocity{}, target{}, omega{7}, zeta{0.7};
  double step(double dt) {
    if (!(dt > 0 && dt <= 0.02) || !(omega > 0) || zeta < 0)
      throw std::invalid_argument("bad spring parameters");
    auto acceleration = -2*zeta*omega*velocity - omega*omega*(position-target);
    velocity += acceleration * dt;
    position += velocity * dt;
    return position;
  }
};
class FixedStep {
  double accumulator_{0};
  double step_;
  int max_steps_;
public:
  FixedStep(double step=1.0/120, int max_steps=8): step_(step), max_steps_(max_steps) {
    if (!(step > 0) || max_steps < 1) throw std::invalid_argument("bad clock");
  }
  template<class F> int advance(double real_dt, F simulate) {
    if (real_dt < 0 || !std::isfinite(real_dt)) throw std::invalid_argument("bad elapsed");
    accumulator_ += real_dt;
    int iterations = 0;
    while (accumulator_ + 1e-12 >= step_ && iterations < max_steps_) {
      simulate(step_);
      accumulator_ -= step_;
      ++iterations;
    }
    return iterations;
  }
  double alpha() const { return std::min(1.0, accumulator_ / step_); }
};
} // namespace anim
