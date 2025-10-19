"use client"

import * as React from "react"
import { AsYouType, parsePhoneNumberFromString, CountryCode, getCountries, getCountryCallingCode } from 'libphonenumber-js'
import { Input } from "./input"
import { Button } from "./button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./dropdown-menu"
import { ChevronDown, Search } from "lucide-react"
import { cn } from "../lib/utils"

// Generate country flag emoji from country code
const getCountryFlag = (countryCode: CountryCode): string => {
  return countryCode
    .toUpperCase()
    .replace(/./g, char => String.fromCodePoint(char.charCodeAt(0) + 127397))
}

// Get country name from country code using browser's built-in Intl.DisplayNames
const getCountryName = (countryCode: CountryCode): string => {
  try {
    const displayNames = new Intl.DisplayNames(['en'], { type: 'region' })
    return displayNames.of(countryCode) || countryCode
  } catch {
    // Fallback for unsupported country codes
    return countryCode
  }
}

// Generate all countries from libphonenumber-js
const getAllCountries = () => {
  return getCountries().map(countryCode => ({
    code: countryCode,
    name: getCountryName(countryCode),
    flag: getCountryFlag(countryCode),
    dialCode: `+${getCountryCallingCode(countryCode)}`
  })).sort((a, b) => a.name.localeCompare(b.name))
}

const COUNTRIES = getAllCountries()

export interface PhoneInputProps {
  value?: string
  onChange?: (value: string | undefined) => void
  defaultCountry?: CountryCode
  className?: string
  placeholder?: string
  disabled?: boolean
}

const PhoneInput = React.forwardRef<HTMLInputElement, PhoneInputProps>(
  ({ 
    className, 
    value = '', 
    onChange, 
    defaultCountry = 'US', 
    placeholder = "Enter phone number", 
    disabled = false, 
    ...props 
  }, ref) => {
    const [selectedCountry, setSelectedCountry] = React.useState<CountryCode>(defaultCountry)
    const [inputValue, setInputValue] = React.useState('')
    const [isDropdownOpen, setIsDropdownOpen] = React.useState(false)
    const [searchQuery, setSearchQuery] = React.useState('')
    const [highlightedIndex, setHighlightedIndex] = React.useState(-1)

    // Find country data
    const currentCountry = COUNTRIES.find(c => c.code === selectedCountry) || COUNTRIES[0]!
    
    // Filter countries based on search query
    const filteredCountries = React.useMemo(() => {
      if (!searchQuery.trim()) return COUNTRIES
      
      const query = searchQuery.toLowerCase()
      return COUNTRIES.filter(country => 
        country.name.toLowerCase().includes(query) ||
        country.dialCode.includes(query) ||
        country.code.toLowerCase().includes(query)
      )
    }, [searchQuery])

    // Initialize input value from props
    React.useEffect(() => {
      if (value) {
        try {
          const phoneNumber = parsePhoneNumberFromString(value)
          if (phoneNumber) {
            setSelectedCountry(phoneNumber.country || defaultCountry)
            setInputValue(phoneNumber.nationalNumber)
          } else {
            setInputValue(value)
          }
        } catch {
          setInputValue(value)
        }
      }
    }, [value, defaultCountry])

    // Reset highlighted index when filtered countries change
    React.useEffect(() => {
      setHighlightedIndex(-1)
    }, [filteredCountries])

    // Reset search when dropdown closes
    React.useEffect(() => {
      if (!isDropdownOpen) {
        setSearchQuery('')
        setHighlightedIndex(-1)
      }
    }, [isDropdownOpen])

    // Handle country selection
    const handleCountrySelect = (country: typeof COUNTRIES[0]) => {
      setSelectedCountry(country.code)
      setIsDropdownOpen(false)
      setSearchQuery('')
      setHighlightedIndex(-1)
      
      // Format existing number for new country
      if (inputValue) {
        const formatter = new AsYouType(country.code)
        const formatted = formatter.input(inputValue)
        setInputValue(formatted)
        
        // Get E.164 format for onChange
        const phoneNumber = formatter.getNumber()
        onChange?.(phoneNumber?.number)
      }
    }

    // Handle keyboard navigation
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (!isDropdownOpen) return

      switch (e.key) {
        case 'ArrowDown':
          e.preventDefault()
          setHighlightedIndex(prev => 
            prev < filteredCountries.length - 1 ? prev + 1 : 0
          )
          break
        case 'ArrowUp':
          e.preventDefault()
          setHighlightedIndex(prev => 
            prev > 0 ? prev - 1 : filteredCountries.length - 1
          )
          break
        case 'Enter':
          e.preventDefault()
          if (highlightedIndex >= 0 && highlightedIndex < filteredCountries.length) {
            handleCountrySelect(filteredCountries[highlightedIndex]!)
          }
          break
        case 'Escape':
          e.preventDefault()
          setIsDropdownOpen(false)
          break
      }
    }

    // Handle input change
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const input = e.target.value
      
      // Use AsYouType formatter for real-time formatting
      const formatter = new AsYouType(selectedCountry)
      const formatted = formatter.input(input)
      
      setInputValue(formatted)
      
      // Get the parsed phone number for validation and E.164 format
      const phoneNumber = formatter.getNumber()
      onChange?.(phoneNumber?.number)
    }

    // Handle paste events to extract phone numbers
    const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
      const pastedText = e.clipboardData.getData('text')
      
      try {
        // Try to parse as international number first
        const phoneNumber = parsePhoneNumberFromString(pastedText)
        if (phoneNumber) {
          e.preventDefault()
          setSelectedCountry(phoneNumber.country || selectedCountry)
          setInputValue(phoneNumber.nationalNumber)
          onChange?.(phoneNumber.number)
          return
        }
      } catch {
        // Let default paste behavior handle it
      }
    }

    return (
      <div className={cn("relative flex", className)} onKeyDown={handleKeyDown}>
        {/* Country Dropdown */}
        <DropdownMenu open={isDropdownOpen} onOpenChange={setIsDropdownOpen}>
          <DropdownMenuTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="h-10 px-3 rounded-r-none border-r-0 flex items-center gap-2"
              disabled={disabled}
            >
              <span className="text-base">{currentCountry.flag}</span>
              <span className="text-sm font-mono">{currentCountry.dialCode}</span>
              <ChevronDown className="h-3 w-3 opacity-50" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start" className="w-80 max-h-80 p-0">
            {/* Search Input */}
            <div className="p-2 border-b">
              <div className="relative">
                <Search className="absolute left-2 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  placeholder="Search countries..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8 h-8"
                  autoFocus
                />
              </div>
            </div>
            
            {/* Countries List */}
            <div className="max-h-60 overflow-y-auto">
              {filteredCountries.length === 0 ? (
                <div className="p-4 text-sm text-muted-foreground text-center">
                  No countries found
                </div>
              ) : (
                filteredCountries.map((country, index) => (
                  <DropdownMenuItem
                    key={country.code}
                    onClick={() => handleCountrySelect(country)}
                    className={cn(
                      "flex items-center gap-3 px-3 py-2 cursor-pointer",
                      index === highlightedIndex && "bg-accent"
                    )}
                  >
                    <span className="text-base">{country.flag}</span>
                    <span className="flex-1 text-sm">{country.name}</span>
                    <span className="text-sm font-mono text-muted-foreground">
                      {country.dialCode}
                    </span>
                  </DropdownMenuItem>
                ))
              )}
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Phone Input */}
        <Input
          ref={ref}
          type="tel"
          value={inputValue}
          onChange={handleInputChange}
          onPaste={handlePaste}
          placeholder={placeholder}
          disabled={disabled}
          className="rounded-l-none border-l-0 flex-1"
          {...props}
        />
      </div>
    )
  }
)

PhoneInput.displayName = "PhoneInput"

export { PhoneInput }
