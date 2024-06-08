pub use euclid;

pub type Size = euclid::default::Size2D<f32>;
pub type Box2D = euclid::default::Box2D<f32>;
pub type Rect = euclid::default::Rect<f32>;

pub mod layout {
    // use smallvec::SmallVec;

    // #[derive(Debug)]
    // pub struct RowItem {
    //     width: f32,
    // }

    use crate::{Box2D, Rect};

    #[derive(Default, Debug)]
    struct RowSegment {
        x: f32,
        count: usize,
        width: f32,
    }

    #[derive(Default, Debug)]
    pub struct RowLayout {
        // items: SmallVec<[RowItem; 20]>,
        gap: f32,
        start: RowSegment,
        end: RowSegment,
        bounds: Box2D,
    }

    impl RowLayout {
        pub fn new(bounds: Rect) -> Self {
            let bounds = bounds.to_box2d();
            Self {
                gap: 0.0,
                start: RowSegment {
                    x: bounds.min.x,
                    count: 0,
                    width: 0.0,
                },
                end: RowSegment {
                    x: bounds.max.x,
                    count: 0,
                    width: 0.0,
                },
                bounds,
            }
        }

        pub fn set_gap(&mut self, gap: f32) {
            self.gap = gap;
        }

        pub fn start_width(&self) -> f32 {
            self.start.width + self.start.count.saturating_sub(1) as f32 * self.gap
        }

        pub fn end_width(&self) -> f32 {
            self.end.width + self.end.count.saturating_sub(1) as f32 * self.gap
        }

        pub fn push_start(&mut self, width: f32) -> f32 {
            let x = self.start.x;
            self.start.x += width;
            self.start.width += width;
            self.start.x += self.gap;
            self.start.count += 1;
            x
        }

        pub fn set_center(&mut self, width: f32) -> f32 {
            let rect = self.bounds.to_rect();
            let center_x = rect.size.width / 2.0;
            center_x - width / 2.0
        }

        pub fn push_end(&mut self, width: f32) -> f32 {
            self.end.x -= width;
            let x = self.end.x;
            self.end.width += width;
            self.end.x -= self.gap;
            self.end.count += 1;
            x
        }
    }

    pub fn row() {}
}
