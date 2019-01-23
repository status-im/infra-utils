--------------------------------------------------------------------------------
-- encoding configuration
--------------------------------------------------------------------------------

local base48Alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
local base32Alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
local base32PadMap = { "", "======", "====", "===", "=" }

--------------------------------------------------------------------------------
-- encoding function for base58
--------------------------------------------------------------------------------

local function encode_base58(s)
	local q, b
	local et = {}
	local zn = 0 	-- number of leading zero bytes in s
	-- assume s is a large, little-endian binary number
	-- with base256 digits (each byte is a "digit")
	local nt = {} -- number to divide in base 256, big endian
	local dt = {} -- result of nt // 58, in base 256
	local more = true  -- used to count leading zero bytes
	for i = 1, #s do
		b = string.byte(s, i)
		if more and b == 0 then
			zn = zn + 1
		else
			more = false
		end
		nt[i] = b
	end
	if #s == zn then --take care of strings empty or with only nul bytes
		return string.rep('1', zn)
	end
	more = true
	while more do
		local r = 0
		more = false
		for i = 1, #nt do
			b = nt[i] + (256 * r)
			q = b // 58
			-- if q is not null at least once, we are good
			-- for another division by 58
			more = more or q > 0
			r = b % 58
			dt[i] = q
		end
		-- r is the next base58 digit. insert it before previous ones
		-- to get a big-endian base58 number
		table.insert(et, 1, string.char(string.byte(base48Alphabet, r+1)))
		-- now copy dt into nt before another round of division by 58
		nt = {}
		for i = 1, #dt do nt[i] = dt[i] end
		dt = {}
	end--while
	-- don't forget the leading zeros ('1' is digit 0 in bitcoin base58 alphabet)
	return string.rep('1', zn) .. table.concat(et)
end

--------------------------------------------------------------------------------
-- various helpers for base32 decoding
--------------------------------------------------------------------------------

local function number_to_bit( num, length )
   local bits = {}

   while num > 0 do
      local rest = math.floor( math.fmod( num, 2 ) )
      table.insert( bits, rest )
      num = ( num - rest ) / 2
   end

   while #bits < length do
      table.insert( bits, "0" )
   end

   return string.reverse( table.concat( bits ) )
end

local function ignore_set( str, set )
   if set then
      str = str:gsub( "["..set.."]", "" )
   end
   return str
end

local function pure_from_bit( str )
   return ( str:gsub( '........', function ( cc )
               return string.char( tonumber( cc, 2 ) )
            end ) )
end

local function unexpected_char_error( str, pos )
   local c = string.sub( str, pos, pos )
   return string.format( "unexpected character at position %d: '%s'", pos, c )
end

--------------------------------------------------------------------------------
-- generic function to decode and encode base32/base64
--------------------------------------------------------------------------------

local function from_basexx( str, alphabet, bits )
   local result = {}
   for i = 1, #str do
      local c = string.sub( str, i, i )
      if c ~= '=' then
         local index = string.find( alphabet, c, 1, true )
         if not index then
            return nil, unexpected_char_error( str, i )
         end
         table.insert( result, number_to_bit( index - 1, bits ) )
      end
   end

   local value = table.concat( result )
   local pad = #value % 8
   return pure_from_bit( string.sub( value, 1, #value - pad ) )
end

function decode_base32( str, ignore )
   str = string.upper(str)
   str = ignore_set( str, ignore )
   return from_basexx( string.upper( str ), base32Alphabet, 5 )
end

--------------------------------------------------------------------------------
-- testing
--------------------------------------------------------------------------------

print(encode_base58('test'))
print(decode_base32('ORSXG5A='))
