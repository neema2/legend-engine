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

package org.finos.legend.pure.runtime.java.extension.functions.compiled;

import org.eclipse.collections.api.list.ListIterable;
import org.finos.legend.pure.m3.exception.PureExecutionException;
import org.finos.legend.pure.m4.coreinstance.CoreInstance;
import org.finos.legend.pure.runtime.java.compiled.generation.processors.support.Pure;

import java.time.ZonedDateTime;

public class FunctionsGen
{
    @Pure
    public static ZonedDateTime timeslice(ZonedDateTime timestamp, String interval, String timezone)
    {
        throw new PureExecutionException("The function 'timeslice' is not implemented in Pure. It should be processed by the execution plans.");
    }

    @Pure
    public static ZonedDateTime timeslice(ZonedDateTime timestamp, String interval)
    {
        return timeslice(timestamp, interval, null);
    }
}
