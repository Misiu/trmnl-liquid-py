# frozen_string_literal: true

require "json"
require "trmnl/liquid"

# trmnl-liquid 0.8.2 intends to fall back when ActionView/Rails helpers are not
# available, but Filters references RailsHelpers without defining it first.
# Define an empty module so respond_to? is false and the gem executes its own
# Fallback implementation. This keeps Rails/I18n out of the baseline oracle.
module TRMNL
  module Liquid
    module RailsHelpers
    end unless const_defined?(:RailsHelpers, false)
  end
end

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
