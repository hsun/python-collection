#!/usr/bin/env ruby

# == Synopsis
#   This is a sample description of the application.
#   Blah blah blah.
#
# == Examples
#   This command does blah blah blah.
#     chart.rb foo.txt
#
#   Other examples:
#     chart.rb -q bar.doc
#     chart.rb --verbose foo.html
#
# == Usage
#   chart.rb [options] source_file
#
#   For help use: chart.rb -h
#
# == Options
#   -h, --help          Displays help message
#   -v, --version       Display the version, then exit
#   -q, --quiet         Output as little as possible, overrides verbose
#   -V, --verbose       Verbose output
#   TO DO - add additional options
#
# == Author
#   YourName
#
# == Copyright
#   Copyright (c) 2007 YourName. Licensed under the MIT License:
#   http://www.opensource.org/licenses/mit-license.php


# TO DO - replace all chart.rb with your app name
# TO DO - replace all YourName with your actual name
# TO DO - update Synopsis, Examples, etc
# TO DO - change license if necessary


require 'optparse'
require 'rdoc/usage'
require 'ostruct'
require 'date'
require 'rubygems'
require "watir"


class App
  VERSION = '0.0.1'

  attr_reader :options

  def initialize(arguments, stdin)
    @arguments = arguments
    @stdin = stdin

    # Set defaults
    @options = OpenStruct.new
    @options.verbose = false
    @options.quiet = false
    @options.symbol = nil
    @options.timeline = nil   
    # TO DO - add additional defaults
  end

  # Parse options, check arguments, then process the command
  def run

    if parsed_options? && arguments_valid? then

      puts "Start at #{DateTime.now}\n\n" if @options.verbose

      output_options if @options.verbose # [Optional]

      process_arguments
      process_command

      puts "\nFinished at #{DateTime.now}" if @options.verbose

    else
      output_usage
    end

  end

  protected

    def parsed_options?

      # Specify options
      opts = OptionParser.new
      opts.on('-v', '--version')    { output_version ; exit 0 }
      opts.on('-h', '--help')       { output_help }
      opts.on('-V', '--verbose')    { @options.verbose = true }
      opts.on('-q', '--quiet')      { @options.quiet = true }
      opts.on('-s', '--symbol [SYMBOL]') do |symbol|
         @options.symbol = symbol
      end
      opts.on('-t', '--timeline [TL]') do |tl|
         @options.timeline = tl
      end
      # TO DO - add additional options

      opts.parse!(@arguments)
      process_options
      true
    end

    # Performs post-parse processing on options
    def process_options
      @options.verbose = false if @options.quiet
    end

    def output_options
      puts "Options:\n"

      @options.marshal_dump.each do |name, val|
        puts "  #{name} = #{val}"
      end
    end

    # True if required arguments were provided
    def arguments_valid?
      # TO DO - implement your real logic here
      true
    end

    # Setup the arguments
    def process_arguments
      # TO DO - place in local vars, etc
    end

    def output_help
      output_version
      RDoc::usage() #exits app
    end

    def output_usage
      RDoc::usage('usage') # gets usage from comments above
    end

    def output_version
      puts "#{File.basename(__FILE__)} version #{VERSION}"
    end

    def process_command

        start_page = "http://stockcharts.com/h-sc/ui?s=#{@options.symbol}"

	Watir::Browser.default = 'safari'
        br = Watir::Browser.new
        br.goto(start_page)

        if @options.timeline == 'l' then
            puts "Show 3 year trends.."
            br.select_list(:id, "period2").select_value("W")
            br.select_list(:id, "dataRange").select_value("predef:3|0|0")
            br.select_list(:id, "symStyle").select("Line (solid)")
        elsif @options.timeline == 'm' then
            puts "Show 1 year trends.."
            br.select_list(:id, "period2").select_value("D")
            br.select_list(:id, "dataRange").select_value("predef:1|0|0")
            br.select_list(:id, "symStyle").select("Candlesticks")
        elsif @options.timeline == 's' then
            puts "Show 3 month trends.."
            br.select_list(:id, "period2").select_value("D")
            br.select_list(:id, "dataRange").select_value("predef:0|3|0")
            br.select_list(:id, "symStyle").select("Candlesticks")
        else
            puts "Show 6 month trends.."
            br.select_list(:id, "period2").select_value("D")
            br.select_list(:id, "dataRange").select_value("predef:0|6|0")
            br.select_list(:id, "symStyle").select("Candlesticks")
        end

        br.select_list(:id, "chartSize").select("Landscape")
        br.select_list(:id, "showVolume").select_value("separate")
        
        br.select_list(:id, "overType_0").select_value("SMA")
        br.text_field(:id, "overArgs_0").set("50")
        
        br.select_list(:id, "overType_1").select_value("SMA")
        br.text_field(:id, "overArgs_1").set("200")

        br.select_list(:id, "indType_0").select_value("STOFULL")
        br.text_field(:id, "indArgs_0").set("10,3,3")
        br.select_list(:id, "indLoc_0").select_value("below")

        br.select_list(:id, "indType_1").select_value("RSI")
        br.text_field(:id, "indArgs_1").set("10")
        br.select_list(:id, "indLoc_1").select_value("below")

        br.select_list(:id, "indType_2").select_value("MACD")
        br.text_field(:id, "indArgs_2").set("12,26,9")
        br.select_list(:id, "indLoc_2").select_value("below")
        
        br.button(:value, "Update").click
    end

    def process_standard_input
      input = @stdin.read
      # TO DO - process input

      # [Optional]
      #@stdin.each do |line|
      #  # TO DO - process each line
      #end
    end
end


# TO DO - Add your Modules, Classes, etc


# Create and run the application
app = App.new(ARGV, STDIN)
app.run


