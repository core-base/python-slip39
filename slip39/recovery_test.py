import codecs
import csv
import logging
import os
import pytest
import math
import cmath

import shamir_mnemonic

from .api		import create, account
from .recovery		import recover, recover_bip39, shannon_entropy, signal_entropy
from .recovery.entropy	import fft, dft, idft, dft_magnitude, dft_on_real
from .dependency_test	import substitute, nonrandom_bytes, SEED_XMAS, SEED_ONES

log				= logging.getLogger( __package__ )

groups_example			= dict( one = (1,1), two = (1,1), fam = (2,4), fren = (3,5) )


@substitute( shamir_mnemonic.shamir, 'RANDOM_BYTES', nonrandom_bytes )
def test_recover():
    details			= create(
        "recovery test", 2, groups_example, SEED_XMAS
    )
    #import json
    #print( json.dumps( details.groups, indent=4 ))
    assert details.groups == {
        "one": (
            1,
            [
                "academic acid acrobat romp chubby client grief judicial pulse domain flip elevator become spirit heat patent hawk remove pickup boring"
            ]
        ),
        "two": (
            1,
            [
                "academic acid beard romp away ancient domain jacket early admit true disaster manual sniff seafood guest stick grumpy blessing unknown"
            ]
        ),
        "fam": (
            2,
            [
                "academic acid ceramic roster density snapshot crush modify born plastic greatest victim merit weapon general cover wits cradle quick emphasis",
                "academic acid ceramic scared brother carve scout stay repeat that fumes tendency junior clay freshman rhyme infant enlarge puny decent",
                "academic acid ceramic shadow class findings zero blessing sidewalk drink jump hormone advocate flip install alpha ugly speak prospect solution",
                "academic acid ceramic sister aluminum obesity blue furl grownup island educate junk traveler listen evidence merit grant python purchase piece"
            ]
        ),
        "fren": (
            3,
            [
                "academic acid decision round academic academic academic academic academic academic academic academic academic academic academic academic academic ranked flame amount",
                "academic acid decision scatter change pleasure dive cricket class impulse lungs hour invasion strike mustang friendly divorce corner penalty fawn",
                "academic acid decision shaft disaster python expand math typical screw rumor research unusual segment install curly debut shadow orange museum",
                "academic acid decision skin browser breathe intimate picture smirk railroad equip spirit nervous capital teaspoon hybrid angel findings hunting similar",
                "academic acid decision snake angel phrase gums response tracks carve secret bucket liquid dictate enemy decrease dance early weapon season"
            ]
        )
    }
    assert recover( details.groups['one'][1] + details.groups['fren'][1][:3] ) == SEED_XMAS

    # Enough correct number of mnemonics must be provided (extras ignored)
    with pytest.raises(shamir_mnemonic.MnemonicError) as excinfo:
        recover( details.groups['one'][1] + details.groups['fren'][1][:2] )
    assert "Wrong number of mnemonics" in str(excinfo.value)

    assert recover( details.groups['one'][1] + details.groups['fren'][1][:4] ) == SEED_XMAS

    # Invalid mnemonic phrases are rejected (one word changed)
    with pytest.raises(shamir_mnemonic.MnemonicError) as excinfo:
        recover( details.groups['one'][1] + details.groups['fren'][1][:2] + [
            "academic acid academic axle crush swing purple violence teacher curly total equation clock mailman display husband tendency smug laundry laundry"
        ])
    assert "Invalid mnemonic checksum" in str(excinfo.value)

    # Duplicate mnemonics rejected/ignored
    with pytest.raises(shamir_mnemonic.MnemonicError) as excinfo:
        recover( details.groups['one'][1] + details.groups['fren'][1][:2] + details.groups['fren'][1][:1] )
    assert "Wrong number of mnemonics" in str(excinfo.value)

    # Mnemonics from another SLIP-39 rejected
    with pytest.raises(shamir_mnemonic.MnemonicError) as excinfo:
        recover( details.groups['one'][1] + details.groups['fren'][1][:2] + [
            "academic acid academic axle crush swing purple violence teacher curly total equation clock mailman display husband tendency smug laundry disaster"
        ])
    assert "Invalid set of mnemonics" in str(excinfo.value)


@substitute( shamir_mnemonic.shamir, 'RANDOM_BYTES', nonrandom_bytes )
def test_recover_bip39():
    """Go through the 3 methods for producing accounts from the same 0xffff...ffff Seed Entropy."""

    # Get BIP-39 Seed generated from Mnemonic Entropy + passphrase
    bip39seed			= recover_bip39( 'zoo ' * 11 + 'wrong' )
    assert codecs.encode( bip39seed, 'hex_codec' ).decode( 'ascii' ) \
        == 'b6a6d8921942dd9806607ebc2750416b289adea669198769f2e15ed926c3aa92bf88ece232317b4ea463e84b0fcd3b53577812ee449ccc448eb45e6f544e25b6'
    details_bip39		= create(
        "bip39 recovery test", 2, groups_example, master_secret=bip39seed,
    )
    #import json
    #print( json.dumps( details_bip39.groups, indent=4 ))
    assert details_bip39.groups == {
        "one": (
            1,
            [
                "academic acid acrobat romp academic angel email prospect endorse strategy debris award strike frost actress facility legend safari pistol"
                " mouse hospital identify unwrap talent entrance trust cause ranked should impulse avoid fangs various radar dilemma indicate says rich work"
                " presence jerky glance hesitate huge depend tension loan tolerate news agree geology phrase random simple finger alarm depart inherit grin"
            ]
        ),
        "two": (
            1,
            [
                "academic acid beard romp acne floral cricket answer debris making decorate square withdraw empty decorate object artwork tracks rocky tolerate"
                " syndrome decorate predator sweater ordinary pecan plastic spew facility predator miracle change solution item lizard testify coal excuse lecture"
                " exercise hamster hand crystal rainbow indicate phantom require satisfy flame acrobat detect closet patent therapy overall muscle spill adjust unhappy"
            ]
        ),
        "fam": (
            2,
            [
                "academic acid ceramic roster acquire again tension ugly edge profile custody geology listen hazard smug branch adequate fishing simple adapt fancy"
                " hour method emperor tactics float quiet location satoshi guilt fantasy royal machine dictate squeeze devote oven eclipse writing level sheriff"
                " teacher purchase building veteran spirit woman realize width vanish scholar jewelry desktop stilt random rhyme debut premium theater",
                "academic acid ceramic scared acid space fantasy breathe true recover privacy tactics boring harvest punish swimming leader talent exchange diet"
                " enforce vanish volume organize coastal emperor change intend club scene intimate upgrade dragon burning lily huge market calcium forecast holiday"
                " merit method type ruler equip retailer pancake paces thorn worthy always story promise clock staff floral smart iris repair",
                "academic acid ceramic shadow acne rumor decent elder aspect lizard obesity friendly regular aircraft beyond military campus employer seafood cover"
                " ivory dough galaxy victim diminish average music cause behavior declare brave toxic visual academic include lilac repair morning rapids building"
                " kernel herald careful helpful move hawk flash glimpse seafood listen writing rocky browser change hybrid diet organize system wrote",
                "academic acid ceramic sister academic both legend raspy pecan mixed broken tenant critical again imply finance pacific single echo capital hesitate"
                " piece disease crush slush belong airline smug voice organize dryer standard emission curious charity swing pitch senior behavior vintage chemical"
                " cage editor rebuild costume adult ancestor erode steady makeup depart carpet level sympathy being soldier glimpse airport picture"
            ]
        ),
        "fren": (
            3,
            [
                "academic acid decision round academic academic academic academic academic academic academic academic academic academic academic academic academic"
                " academic academic academic academic academic academic academic academic academic academic academic academic academic academic academic academic"
                " academic academic academic academic academic academic academic academic academic academic academic academic academic academic academic academic"
                " academic academic academic academic academic academic academic aviation endless plastic",
                "academic acid decision scatter acid ugly raspy famous swimming else length gray raspy brother fake aunt auction premium military emphasis perfect"
                " surprise class suitable crunch famous burden military laundry inmate regret elder mixture tenant taught smirk voter process steady artist equip"
                " jury carve acrobat western cylinder gasoline artwork snapshot ancestor object cinema market species platform iris dragon dive medal",
                "academic acid decision shaft acid carbon credit cards rich living humidity peasant source triumph magazine ladle ruin ocean aspect curious round"
                " main evoke deny stadium zero discuss union strike pencil golden silent geology display wrap peanut listen aide learn juice decision plot bike example"
                " obesity ancient square pistol twice sister hour amuse human hobo hospital escape expect wildlife luck",
                "academic acid decision skin academic vanish olympic evoke gesture rumor unfair scroll grasp very steady include smell diploma package guest greatest"
                " firm humidity trial width priest class large photo sniff survive machine usher stick capacity heat improve predator float iris jacket soldier apart"
                " excuse garden cleanup realize permit dough script veteran crazy theater rival secret drink kernel lips pants",
                "academic acid decision snake acid vegan darkness bucket benefit therapy valuable impulse canyon swing distance vampire round losing twin medal treat"
                " amount fiction hush remind faint distance custody device believe campus guest preach mule exhaust regular short phrase column rescue steady float"
                " mixture testify taught fiction usher snake museum detailed agree intend inherit likely typical blimp symbolic prayer course"
            ]
        )
    }
    assert recover( details_bip39.groups['one'][1][:] + details_bip39.groups['fren'][1][:3] ) == bip39seed

    [(eth,btc)] = details_bip39.accounts
    assert eth.address == "0xfc2077CA7F403cBECA41B1B0F62D91B5EA631B5E"
    assert btc.address == "bc1qk0a9hr7wjfxeenz9nwenw9flhq0tmsf6vsgnn2"

    #
    # Now, get the exact same derived accounts, but by passing the BIP-39 Seed Entropy (not the generated Seed!)
    #
    bip39entropy		= recover_bip39( 'zoo ' * 11 + 'wrong', as_entropy=True )
    assert codecs.encode( bip39entropy, 'hex_codec' ).decode( 'ascii' ) \
        == 'ff' * 16
    details_bip39entropy	= create(
        "bip39 recovery test", 2, dict( one = (1,1), two = (1,1), fam = (2,4), fren = (3,5) ),
        master_secret=bip39entropy,
        using_bip39=True,
    )
    assert recover( details_bip39entropy.groups['one'][1][:] + details_bip39entropy.groups['fren'][1][:3] ) == bip39entropy

    [(eth,btc)] = details_bip39entropy.accounts
    assert eth.address == "0xfc2077CA7F403cBECA41B1B0F62D91B5EA631B5E"
    assert btc.address == "bc1qk0a9hr7wjfxeenz9nwenw9flhq0tmsf6vsgnn2"

    #
    # Finally, test that the basic SLIP-39 encoding and derivation using the raw Seed Entropy is
    # different, and yields the expected well-known accounts.
    #
    details_slip39		= create(
        "bip39 recovery test -- all ones in SLIP-39", 2, groups_example, SEED_ONES,
    )
    import json
    print( json.dumps( details_slip39.groups, indent=4 ))
    assert details_slip39.groups == {
        "one": (
            1,
            [
                "academic acid acrobat romp change injury painting safari drug browser trash fridge busy finger standard angry similar overall prune ladybug"
            ]
        ),
        "two": (
            1,
            [
                "academic acid beard romp believe impulse species holiday demand building earth warn lunar olympic clothes piece campus alpha short endless"
            ]
        ),
        "fam": (
            2,
            [
                "academic acid ceramic roster desire unwrap depend silent mountain agency fused primary clinic alpha database liberty silver advance replace medical",
                "academic acid ceramic scared column screw hawk dining invasion bumpy identify anxiety august sunlight intimate satoshi hobo traveler carbon class",
                "academic acid ceramic shadow believe revenue type class station domestic already fact desktop penalty omit actress rumor beaver forecast group",
                "academic acid ceramic sister actress mortgage random talent device clogs craft volume cargo item scramble easy grumpy wildlife wrist simple"
            ]
        ),
        "fren": (
            3,
            [
                "academic acid decision round academic academic academic academic academic academic academic academic academic academic academic academic academic ranked flame amount",
                "academic acid decision scatter biology trial escape element unfair cage wavy afraid provide blind pitch ultimate hybrid gravity formal voting",
                "academic acid decision shaft crunch glance exclude stilt grill numb smug stick obtain raisin force theater duke taught license scramble",
                "academic acid decision skin disaster mama alive nylon mansion listen cowboy suitable crisis pancake velvet aviation exhaust decent medal dominant",
                "academic acid decision snake aunt frozen flip crystal crystal observe equip maximum maiden dragon wine crazy nervous crystal profile fiction"
            ]
        )
    }

    # These are the well-known SLIP-39 0xffff...ffff Seed accounts
    [(eth,btc)] = details_slip39.accounts
    assert eth.address == "0x824b174803e688dE39aF5B3D7Cd39bE6515A19a1"
    assert btc.address == "bc1q9yscq3l2yfxlvnlk3cszpqefparrv7tk24u6pl"

    # And ensure that the SLIP-39 encoding of the BIP-39 "zoo zoo ... wrong" w/ BIP-39
    # Entropy was identically to the raw SLIP-39 encoding.
    assert details_slip39.groups == details_bip39entropy.groups


def into_boolean( val, truthy=(), falsey=() ):
    """Check if the provided numeric or str val content is truthy or falsey; additional tuples of
    truthy/falsey lowercase values may be provided.  The empty/whitespace string is Falsey."""
    if isinstance( val, (int,float,bool)):
        return bool( val )
    assert isinstance( val, str )
    if val.strip().lower() in ( 't', 'true', 'y', 'yes' ) + truthy:
        return True
    elif val.strip().lower() in ( 'f', 'false', 'n', 'no', '' ) + falsey:
        return False
    raise ValueError( val )


def test_recover_bip39_vectors():
    # Test some BIP-39 encodings that have caused issues for other platforms:
    #
    #   - https://github.com/iancoleman/bip39/issues/58

    # If passphrase is None, signals BIP-39 recover as_entropy, and account generation using_bip39
    # bip39_tests		= [
    #     ['zoo ' * 11 + 'wrong', "", True, (
    #         None, 'bech32', 'bc1qk0a9hr7wjfxeenz9nwenw9flhq0tmsf6vsgnn2')],
    #     ['zoo ' * 11 + 'wrong', "", None, (
    #         None, 'bech32', 'bc1q9yscq3l2yfxlvnlk3cszpqefparrv7tk24u6pl')],
    #     [ 'fruit wave dwarf banana earth journey tattoo true farm silk olive fence', 'banana', True, (
    #         None, 'legacy', '17rxURoF96VhmkcEGCj5LNQkmN9HVhWb7F')]
    # ]
    with open( os.path.join( os.path.splitext( __file__ )[0] + '.csv' )) as bip32_csv:
        bip39_tests		= list( csv.DictReader( bip32_csv, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True ))

    for i,t in enumerate( bip39_tests ):
        log.info( f"Testing: {t!r}" )
        # Decode the entropy; either hex or BIP-39 mnemonics support
        entropy			= t.get( 'entropy' )
        if all( c in '0123456789abcdef' for c in entropy.lower() ):
            master_secret	= codecs.decode( entropy, 'hex_codec' )  # Hex entropy allowed
        else:
            passphrase		= ( t.get( 'passphrase', '' )).strip()
            if into_boolean( t.get( 'using_bip39', False )):
                # When using BIP-39, we obtain the 512-bit seed from the 128/256-bit BIP-39 mnemonic
                # entropy + passphrase, and use that to derive the wallets.
                master_secret	= recover_bip39( entropy, passphrase=passphrase )
            else:
                # For SLIP-39 wallets, we recover the 128/256-bit entropy, which is used directly as the
                # seed to derive the wallets.  The passphrase would be used to secure the SLIP-39
                # mnemonics.
                assert not passphrase, \
                    "row {i+1}: passphrase unsupported unless using_bip39"
                master_secret	= recover_bip39( entropy, passphrase=None, as_entropy=True )

        master_secret_hex	= codecs.encode( master_secret, 'hex_codec' ).decode( 'ascii' )
        log.debug( f"Entropy {entropy!r} ==> {master_secret_hex!r}" )

        # Decode the desired address; 1... and xpub... are legacy, 3... and ypub... are segwit and
        # bc1... and zpub are bech32.
        address			= t.get( 'address' )
        format			= {
            '1': 'legacy',
            'x': 'legacy',
            '3': 'segwit',
            'y': 'segwit',
            'b': 'bech32',
            'z': 'bech32',
        }[address[0]]
        acct			= account(
            master_secret	= master_secret,
            crypto		= "BTC",
            path		= t.get( 'path' ),
            format		= format
        )
        # Finally, generate the account's address or xpubkey
        addresses		= [ acct.address, acct.xpubkey ]
        assert address in addresses, \
            f"row {i+1}: BTC account {address} not in {addresses!r} for entropy {entropy} ==> {master_secret}"


def test_dft():
    print()
    print( "Real-valued samples, recovered from inverse DFT:" )
    x				= [ 2, 3, 5, 7, 11 ]
    print( "vals:  " + ' '.join( f"{f:11.2f}" for f in x ))
    y				= dft( x )
    print( "dft:   " + ' '.join( f"{f:11.2f}" for f in y ))
    z				= idft( y )
    print( "idft:  " + ' '.join( f"{f:11.2f}" for f in z ))
    print( "recov.:" + ' '.join( f"{f:11.2f}" for f in dft_magnitude( z )))

    # Lets determine how dft organizes its output buckets.  Lets find the bucket contain any DC
    # offset, by supplying a 0Hz signal w/ a large DC offset.

    # What about a single full real-valued waveform (complex component is always 0j)?
    print()
    print( "Real-valued signal, 1-4 cycles in 8 samples:" )
    dc				= [1.0] * 8
    print( "DC:     " + ' '.join( f"{f:11.2f}" for f in dc ))
    dft_dc			= dft( dc )
    print( "  DFT:  " + ' '.join( f"{f:11.2f}" for f in dft_dc ))
    print( "  DFT_r:" + ' '.join( f"{f:11.2f}" for f in dft_on_real( dft_dc )))
    assert dft_dc[0] == pytest.approx( 8+0j )
    #1Hz:           1.000          0.707          0.000         -0.707         -1.000         -0.707         -0.000          0.707
    #1Hz_d: -0.000+0.000j   4.000-0.000j  -0.000-0.000j   0.000-0.000j   0.000-0.000j   0.000-0.000j   0.000-0.000j   4.000+0.000j
    oneHz			= [math.sin(+math.pi/2+math.pi*2*i/8) for i in range( 8 )]
    print( "+1Hz:   " + ' '.join( f"{f:11.2f}" for f in oneHz ))
    dft_oneHz			= dft( oneHz )
    print( "  DFT:  " + ' '.join( f"{f:11.2f}" for f in dft_oneHz ))
    fft_oneHz			= fft( oneHz )
    print( "  FFT:  " + ' '.join( f"{f:11.2f}" for f in fft_oneHz ))
    print( "  DFT_r:" + ' '.join( f"{f:11.2f}" for f in dft_on_real( dft_oneHz )))
    #2Hz:           1.000          0.000         -1.000         -0.000          1.000          0.000         -1.000         -0.000
    #2Hz_d: -0.000+0.000j  -0.000-0.000j   4.000-0.000j  -0.000-0.000j   0.000-0.000j   0.000-0.000j   4.000+0.000j   0.000-0.000j
    twoHz			= [math.sin(+math.pi/2+math.pi*2*i/4) for i in range( 8 )]
    print( "+2Hz:   " + ' '.join( f"{f:11.2f}" for f in twoHz ))
    dft_twoHz			= dft( twoHz )
    print( "  DFT:  " + ' '.join( f"{f:11.2f}" for f in dft_twoHz ))
    print( "  DFT_r:" + ' '.join( f"{f:11.2f}" for f in dft_on_real( dft_twoHz )))
    #4Hz:           1.000         -1.000          1.000         -1.000          1.000         -1.000          1.000         -1.000
    #4Hz_d:  0.000+0.000j   0.000-0.000j   0.000-0.000j   0.000-0.000j   8.000+0.000j  -0.000+0.000j   0.000-0.000j  -0.000-0.000j
    forHz			= [math.sin(+math.pi/2+math.pi*2*i/2) for i in range( 8 )]
    print( "+4Hz:   " + ' '.join( f"{f:11.2f}" for f in forHz ))
    dft_forHz			= dft( forHz )
    print( "  DFT:  " + ' '.join( f"{f:11.2f}" for f in dft_forHz ))
    print( "  DFT_r:" + ' '.join( f"{f:11.2f}" for f in dft_on_real( dft_forHz )))
    # Same, but just shifted -PI/2, instead of +PI/2: reverses the highest frequency bucket.
    #4Hz:          -1.000          1.000         -1.000          1.000         -1.000          1.000         -1.000          1.000
    #4Hz_d:  0.000+0.000j   0.000+0.000j  -0.000+0.000j  -0.000+0.000j  -8.000-0.000j   0.000-0.000j  -0.000+0.000j   0.000+0.000j
    forHz			= [math.sin(-math.pi/2-math.pi*2*i/2) for i in range( 8 )]
    print( "-4Hz:   " + ' '.join( f"{f:11.2f}" for f in forHz ))
    dft_forHz			= dft( forHz )
    print( "  DFT:  " + ' '.join( f"{f:11.2f}" for f in dft_forHz ))
    print( "  DFT_r:" + ' '.join( f"{f:11.2f}" for f in dft_on_real( dft_forHz )))

    # So, the frequency buckets are symmetrical, from DC, 1B/N up to (N/2)B/N (which is also
    # -(N/2)B/N), and then back down to -1B/N.  We do complex signals, so we can see signals of the
    # same frequency on +'ve and -'ve side of DC.  Note that -4/8 and +4/8 are indistinguishable --
    # both rotate the complex signal by 1/2 on each steop, so the "direction" of rotation in complex
    # space is not known.  This is why the signal must be filtered; any frequency components at or
    # above B/2 will simply be mis-interpreted as artifacts in other lower frequency buckets.
    N				= 8
    print()
    print( f"Complex signal, 1-4 cycles in {N} samples:" )
    for rot_i,rot in enumerate((0, 1, 2, 3, -4, -3, -2, -1)):  # buckets, in ascending index order
        sig			= [
            # unit-magnitude complex samples, rotated through 2Pi 'rot' times, in N steps
            cmath.rect(
                1, math.pi*2*rot/N*i
            )
            for i in range( N )
        ]
        print( f"{rot:2} cyc.:" + ' '.join( f"{f:11.2f}" for f in sig ))
        dft_sig			= dft( sig )
        print( "  DFT:  " + ' '.join( f"{f:11.2f}" for f in dft_sig ))
        print( "   ABS: " + ' '.join( f"{abs(f):11.2f}" for f in dft_sig ))
        assert dft_sig[rot_i] == pytest.approx( 8+0j )


def test_signal_entropy():
    print()
    entropy			= codecs.decode( 'ff00' * 8, 'hex_codec' )
    signal			= signal_entropy( entropy, 8, 8 )
    assert signal.dB == pytest.approx( 13.11755068 )
    signal			= signal_entropy( SEED_XMAS, 8, 8 )
    assert signal.dB == pytest.approx( 8.712742582 )


def test_shannon_entropy():

    shannon			= shannon_entropy( SEED_ONES )
    shannon			= shannon_entropy( SEED_ONES, overlap=False )
    shannon			= shannon_entropy( SEED_ONES, stride=4 )
    shannon			= shannon_entropy( SEED_ONES, stride=4, overlap=False )

    SEED_ZERO_HEX		= b'00' * 16
    SEED_ZERO			= codecs.decode( SEED_ZERO_HEX, 'hex_codec' )

    shannon			= shannon_entropy( SEED_ONES+SEED_ZERO )
    shannon			= shannon_entropy( SEED_ONES+SEED_ZERO, overlap=False )
    shannon			= shannon_entropy( SEED_ONES+SEED_ZERO, stride=4 )
    shannon			= shannon_entropy( SEED_ONES+SEED_ZERO, stride=4, overlap=False )

    shannon			= shannon_entropy( SEED_ONES+SEED_XMAS )
    shannon			= shannon_entropy( SEED_ONES+SEED_XMAS, overlap=False )
    shannon			= shannon_entropy( SEED_ONES+SEED_XMAS, stride=4 )
    shannon			= shannon_entropy( SEED_ONES+SEED_XMAS, stride=4, overlap=False )

    shannon			= shannon_entropy( SEED_XMAS )
    shannon			= shannon_entropy( SEED_XMAS, stride=16 )
    shannon			= shannon_entropy( SEED_XMAS, stride=16, overlap=False )
    shannon			= shannon_entropy( SEED_XMAS, stride=10 )
    shannon			= shannon_entropy( SEED_XMAS, stride=10, overlap=False )
    shannon			= shannon_entropy( SEED_XMAS, stride=6 )
    shannon			= shannon_entropy( SEED_XMAS, stride=6, overlap=False )
    shannon			= shannon_entropy( SEED_XMAS, stride=4 )
    assert shannon.dB == pytest.approx( -0.29758997 )
    shannon			= shannon_entropy( SEED_XMAS )
    assert shannon.dB == pytest.approx( -40.0 )
    # Now, add some duplicates, reducing the entropy.
    shannon			= shannon_entropy( SEED_XMAS+SEED_XMAS[:3] )
    assert shannon.dB == pytest.approx( -2.5456588 )
    shannon			= shannon_entropy( SEED_XMAS+SEED_XMAS[:4] )
    assert shannon.dB == pytest.approx( -0.66536314 )
    shannon			= shannon_entropy( SEED_XMAS+SEED_XMAS[:5] )
    assert shannon.dB == pytest.approx( 0.694995717 )
    shannon			= shannon_entropy( SEED_XMAS+SEED_XMAS[:6] )
    assert shannon.dB == pytest.approx( 1.73372033 )
