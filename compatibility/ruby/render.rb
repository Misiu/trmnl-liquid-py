# frozen_string_literal: true

require "json"
require "trmnl/liquid"

$stdout.sync = true

def render_case(payload)
  environment = TRMNL::Liquid.new
  template = Liquid::Template.parse(payload.fetch("template"), environment: environment)
  {
    "ok" => true,
    "output" => template.render(payload.fetch("data", {}))
  }
rescue StandardError => error
  {
    "ok" => false,
    "error_class" => error.class.name,
    "error" => error.message
  }
end

ARGF.each_line do |line|
  next if line.strip.empty?

  puts JSON.generate(render_case(JSON.parse(line)))
end
