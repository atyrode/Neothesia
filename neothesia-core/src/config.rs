use std::path::PathBuf;

use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Default, Clone)]
pub struct ColorSchema {
    pub base: (u8, u8, u8),
    pub dark: (u8, u8, u8),
}

#[derive(Serialize, Deserialize)]
pub struct Config {
    #[serde(default = "default_speed_multiplier")]
    pub speed_multiplier: f32,

    #[serde(default = "default_animation_speed")]
    pub animation_speed: f32,

    #[serde(default = "default_playback_offset")]
    pub playback_offset: f32,

    #[serde(default = "default_audio_gain")]
    pub audio_gain: f32,

    #[serde(default = "default_vertical_guidelines")]
    pub vertical_guidelines: bool,

    #[serde(default = "default_horizontal_guidelines")]
    pub horizontal_guidelines: bool,

    #[serde(default = "default_color_schema")]
    pub color_schema: Vec<ColorSchema>,

    #[serde(default)]
    pub background_color: (u8, u8, u8),

    #[serde(default = "default_output")]
    pub output: Option<String>,
    pub input: Option<String>,

    pub soundfont_path: Option<PathBuf>,
    pub last_opened_song: Option<PathBuf>,

    #[serde(default = "default_piano_range")]
    pub piano_range: (u8, u8),
}

impl Default for Config {
    fn default() -> Self {
        Self::new()
    }
}

impl Config {
    pub fn new() -> Self {
        let config: Option<Config> = if let Some(path) = crate::utils::resources::settings_ron() {
            if let Ok(file) = std::fs::read_to_string(path) {
                match ron::from_str(&file) {
                    Ok(config) => Some(config),
                    Err(err) => {
                        log::error!("{:#?}", err);
                        None
                    }
                }
            } else {
                None
            }
        } else {
            None
        };

        config.unwrap_or_else(|| Self {
            speed_multiplier: default_speed_multiplier(),
            animation_speed: default_animation_speed(),
            playback_offset: default_playback_offset(),
            audio_gain: default_audio_gain(),
            vertical_guidelines: default_vertical_guidelines(),
            horizontal_guidelines: default_horizontal_guidelines(),
            color_schema: default_color_schema(),
            background_color: Default::default(),
            output: default_output(),
            input: None,
            soundfont_path: None,
            last_opened_song: None,
            piano_range: default_piano_range(),
        })
    }

    pub fn piano_range(&self) -> std::ops::RangeInclusive<u8> {
        self.piano_range.0..=self.piano_range.1
    }

    pub fn set_output(&mut self, output: Option<String>) {
        self.output = output;
    }

    pub fn set_input<D: std::fmt::Display>(&mut self, v: Option<D>) {
        self.input = v.map(|v| v.to_string());
    }
}

impl Drop for Config {
    fn drop(&mut self) {
        if let Ok(s) = ron::ser::to_string_pretty(self, Default::default()) {
            if let Some(path) = crate::utils::resources::settings_ron() {
                std::fs::create_dir_all(path.parent().unwrap()).ok();
                std::fs::write(path, s).ok();
            }
        }
    }
}

fn default_piano_range() -> (u8, u8) {
    (48, 71)
}

fn default_speed_multiplier() -> f32 {
    1.0
}

fn default_animation_speed() -> f32 {
    400.0
}

fn default_playback_offset() -> f32 {
    0.0
}

fn default_audio_gain() -> f32 {
    0.2
}

fn default_vertical_guidelines() -> bool {
    false
}

fn default_horizontal_guidelines() -> bool {
    false
}

fn default_color_schema() -> Vec<ColorSchema> {
    vec![
        ColorSchema {
            base: (210, 89, 222),
            dark: (125, 69, 134),
        },
        ColorSchema {
            base: (93, 188, 255),
            dark: (48, 124, 255),
        },
        ColorSchema {
            base: (255, 126, 51),
            dark: (192, 73, 0),
        },
        ColorSchema {
            base: (51, 255, 102),
            dark: (0, 168, 2),
        },
        ColorSchema {
            base: (255, 51, 129),
            dark: (48, 124, 255),
        },
        ColorSchema {
            base: (210, 89, 222),
            dark: (125, 69, 134),
        },
    ]
}

fn default_output() -> Option<String> {
    Some("Buildin Synth".into())
}
