// Copyright 2024 Goldman Sachs
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package org.finos.legend.pure.runtime.java.extension.external.relation.shared.window;

import org.eclipse.collections.impl.factory.Lists;
import org.finos.legend.pure.m3.navigation.PrimitiveUtilities;
import org.finos.legend.pure.m3.navigation.ProcessorSupport;
import org.finos.legend.pure.m4.coreinstance.CoreInstance;

public class Frame
{
    FrameType type;
    boolean fromUnbounded;
    boolean fromCurrentRow;
    int offsetFrom;
    boolean toUnbounded;
    boolean toCurrentRow;
    int offsetTo;

    public Frame(FrameType type, boolean fromUnbounded, int offsetTo)
    {
        this.type = type;
        this.fromUnbounded = fromUnbounded;
        this.offsetTo = offsetTo;
    }

    public Frame(FrameType type, boolean fromUnbounded, boolean toUnbounded)
    {
        this.type = type;
        this.fromUnbounded = fromUnbounded;
        this.toUnbounded = toUnbounded;
    }

    public Frame(FrameType type, int offsetFrom, boolean toUnbounded)
    {
        this.type = type;
        this.offsetFrom = offsetFrom;
        this.toUnbounded = toUnbounded;

    }

    public Frame(FrameType type, int offsetFrom, int offsetTo)
    {
        this.type = type;
        this.offsetFrom = offsetFrom;
        this.offsetTo = offsetTo;
    }

    public Frame(FrameType frameType, boolean b, int i, boolean b1, int i1)
    {
        this.type = frameType;
        this.fromUnbounded = b;
        this.offsetFrom = i;
        this.toUnbounded = b1;
        this.offsetTo = i1;
    }
    
    public Frame(FrameType frameType, boolean fromUnbounded, boolean fromCurrentRow, boolean toUnbounded, boolean toCurrentRow, int offsetFrom, int offsetTo)
    {
        this.type = frameType;
        this.fromUnbounded = fromUnbounded;
        this.fromCurrentRow = fromCurrentRow;
        this.offsetFrom = offsetFrom;
        this.toUnbounded = toUnbounded;
        this.toCurrentRow = toCurrentRow;
        this.offsetTo = offsetTo;
    }

    public static Frame build(CoreInstance frameCore, ProcessorSupport processorSupport)
    {
        if (frameCore == null)
        {
            return null;
        }
        FrameType type = processorSupport.instance_instanceOf(frameCore, "meta::pure::functions::relation::Rows") ? FrameType.rows : FrameType.range;
        CoreInstance from = frameCore.getValueForMetaPropertyToOne("offsetFrom");
        CoreInstance to = frameCore.getValueForMetaPropertyToOne("offsetTo");
        boolean fromUn = processorSupport.instance_instanceOf(from, "meta::pure::functions::relation::UnboundedFrameValue");
        boolean toUn = processorSupport.instance_instanceOf(to, "meta::pure::functions::relation::UnboundedFrameValue");
        boolean fromCR = processorSupport.instance_instanceOf(from, "meta::pure::functions::relation::CurrentRowFrameValue");
        boolean toCR = processorSupport.instance_instanceOf(to, "meta::pure::functions::relation::CurrentRowFrameValue");
        Frame result;
        if (fromUn)
        {
            result = toUn ? new Frame(type, fromUn, toUn) : toCR ? new Frame(type, fromUn, false, toUn, true, 0, 0) : new Frame(type, fromUn, (int) PrimitiveUtilities.getIntegerValue(to.getValueForMetaPropertyToOne("value")));
        }
        else if (fromCR)
        {
            result = toUn ? new Frame(type, false, true, toUn, false, 0, 0) : toCR ? new Frame(type, false, true, false, true, 0, 0) : new Frame(type, false, true, false, false, 0, (int) PrimitiveUtilities.getIntegerValue(to.getValueForMetaPropertyToOne("value")));
        }
        else
        {
            result = toUn ? new Frame(type, (int) PrimitiveUtilities.getIntegerValue(from.getValueForMetaPropertyToOne("value")), toUn) : toCR ? new Frame(type, false, false, false, true, (int) PrimitiveUtilities.getIntegerValue(from.getValueForMetaPropertyToOne("value")), 0) : new Frame(type, (int) PrimitiveUtilities.getIntegerValue(from.getValueForMetaPropertyToOne("value")), (int) PrimitiveUtilities.getIntegerValue(to.getValueForMetaPropertyToOne("value")));
        }
        return result;
    }

    public int getLow(int currentRow)
    {
        return fromUnbounded ? 0 : fromCurrentRow ? currentRow : Math.max(0, currentRow - offsetFrom);
    }

    public int getHigh(int currentRow, int maxSize)
    {
        return toUnbounded ? maxSize - 1 : toCurrentRow ? currentRow : Math.min(maxSize - 1, currentRow + offsetTo);
    }

    public CoreInstance convert(ProcessorSupport ps, PrimitiveBuilder primitiveBuilder)
    {
        CoreInstance result = ps.newCoreInstance("", this.type == FrameType.rows ? "meta::pure::functions::relation::Rows" : "meta::pure::functions::relation::Range", null);
        CoreInstance from;
        if (this.fromUnbounded)
        {
            from = ps.newCoreInstance("", "meta::pure::functions::relation::UnboundedFrameValue", null);
        }
        else if (this.fromCurrentRow)
        {
            from = ps.newCoreInstance("", "meta::pure::functions::relation::CurrentRowFrameValue", null);
        }
        else
        {
            from = ps.newCoreInstance("", "meta::pure::functions::relation::FrameIntValue", null);
            from.setKeyValues(Lists.mutable.with("value"), Lists.mutable.with(primitiveBuilder.build(this.offsetFrom)));
        }
        
        CoreInstance to;
        if (this.toUnbounded)
        {
            to = ps.newCoreInstance("", "meta::pure::functions::relation::UnboundedFrameValue", null);
        }
        else if (this.toCurrentRow)
        {
            to = ps.newCoreInstance("", "meta::pure::functions::relation::CurrentRowFrameValue", null);
        }
        else
        {
            to = ps.newCoreInstance("", "meta::pure::functions::relation::FrameIntValue", null);
            to.setKeyValues(Lists.mutable.with("value"), Lists.mutable.with(primitiveBuilder.build(this.offsetTo)));
        }
        
        result.setKeyValues(Lists.mutable.with("offsetFrom"), Lists.mutable.with(from));
        result.setKeyValues(Lists.mutable.with("offsetTo"), Lists.mutable.with(to));
        return result;
    }

    public static interface PrimitiveBuilder
    {
        CoreInstance build(String val);

        CoreInstance build(int val);
    }
}

